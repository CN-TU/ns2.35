# COMAND TO EXECUTE:
# my_command='../../../../../bin/ns varying-senders.tcl ${sender_type} ${congestion_modified}_${sender_type}_${loss} ${congestion} ${loss}' && for congestion in `echo "Newreno Linux/cubic" | tr " " "\n"` ; do for sender_type in `echo "1 2 4 8" | tr " " "\n"` ; do for loss in `echo "0 0.01" | tr " " "\n"` ; do export congestion ; export congestion_modified=`echo ${congestion} | sed 's/Linux\///'` ; export sender_type ; export loss ; sleep 0 && local_command=`bash -c "echo $my_command"` && echo $local_command && eval "$local_command &" ; done ; done ; done

set trace_directory nam_traces
if {[expr {![file exists $trace_directory]}]} {
    file mkdir $trace_directory
}

set number_of_senders [lindex $argv 0]

#Create a simulator object
set ns [new Simulator]

set opt(whiskerdir) ../../../../tcp/remy/rats/new/
set opt(nsrc) $number_of_senders
set opt(accessdelay) 1ms
set opt(accessrate) 1000Mb
set opt(bneckbw) 20Mb
set opt(delay) 49ms
# set opt(delay) 9ms
set opt(infq) 1000
set opt(maxq) 10
set opt(tr) ${trace_directory}/[lindex $argv 1]
set opt(pktsize) 1210
# Run for 10 minutes
# set opt(simtime) 600.0s
set opt(simtime) 600.0s
# Because otherwise the default receive window in ns2 is tiny and congestion is never actually achieved because of the ridiculous receive window.
set opt(rcvwin) 65536
set opt(tcp) TCP/[lindex $argv 2]
# set opt(tcp) TCP/Newreno
# set opt(tcp) TCP/Linux/cubic

set opt(sloss) [lindex $argv 3]

#Open the NAM trace file
if { [info exists opt(tr)] } {
    if {[file exists $opt(tr).nam]} {
        file delete $opt(tr).nam
    }
    set nf [open $opt(tr).nam w]
    $ns namtrace-all $nf
    # $ns trace-all $nf
}

#Define a 'finish' procedure
proc finish {} {
    global ns nf
    $ns flush-trace
    #Close the NAM trace file
    close $nf
    #Execute NAM on the trace file
    # exec nam out.nam &
    exit 0
}

#
# Create a simple dumbbell topology.
#
proc create-dumbbell-topology {} {
    global ns opt s
    for {set i 0} {$i < $opt(nsrc)} {incr i} {
        set s($i) [$ns node]
    }
    set opt(gw) [$ns node]
    set opt(d) [$ns node]
    for {set i 0} {$i < $opt(nsrc)} {incr i} {
#        $ns duplex-link $s($i) $gw 10Mb 1ms DropTail
#        $ns duplex-link $gw $d $bneckbw $delay DropTail
        $ns duplex-link $s($i) $opt(gw) $opt(accessrate) $opt(accessdelay) DropTail
        $ns queue-limit $s($i) $opt(gw) $opt(infq)
        $ns queue-limit $opt(gw) $s($i) $opt(infq)
    }

    set half_delay [expr {[string range $opt(delay) 0 [string length $opt(delay)]-3]/2.0}]ms

    $ns simplex-link $opt(gw) $opt(d) $opt(bneckbw) $half_delay DropTail
    $ns simplex-link $opt(d) $opt(gw) $opt(bneckbw) $half_delay DropTail

    # Stochastic loss
    set loss_random_variable [new RandomVariable/Uniform]
    $loss_random_variable set min_ 0
    $loss_random_variable set max_ 1
    set loss_module [new ErrorModel]
    $loss_module drop-target [new Agent/Null]
    $loss_module set rate_ $opt(sloss)
    $loss_module ranvar $loss_random_variable

    $ns lossmodel $loss_module $opt(gw) $opt(d)

    # if { [info exists opt(tr)] } {
	#     $ns trace-queue $opt(gw) $opt(d)
    # }
    $ns queue-limit $opt(gw) $opt(d) $opt(maxq)
    $ns queue-limit $opt(d) $opt(gw) $opt(infq)
}

proc create-tcp-connections {} {
    global ns opt s tcps
    for {set i 0} {$i < $opt(nsrc)} {incr i} {
        #Setup a TCP connection

        if { [string range $opt(tcp) 0 9] == "TCP/Linux/"} {
            set linuxcc [ string range $opt(tcp) 10 [string length $opt(tcp)] ]
            set opt(tcp) "TCP/Linux"
        }
        # puts [ string range $opt(tcp) 0 12]
        if { [ string range $opt(tcp) 0 12] == "TCP/Rational/" } {
            set ::env(WHISKERS) $opt(whiskerdir)[string range $opt(tcp) 12 [string length $opt(tcp)]]
            set opt(tcp) "TCP/Rational"
            # puts $opt(tcp)
            # echo
        }
        # puts $opt(tcp)
        set tcp [new Agent/$opt(tcp)]
        $tcp set tracewhisk_ 0
        if { [info exists linuxcc] } {
            $ns at 0.0 "$tcp select_ca $linuxcc"
            $ns at 0.0 "$tcp set_ca_default_param linux debug_level 2"
        }
        # set tcp [new Agent/TCP/Newreno]
        # puts $tcp
        $ns attach-agent $s($i) $tcp
        set sink [new Agent/TCPSink]
        $ns attach-agent $opt(d) $sink
        $ns connect $tcp $sink
        $tcp set packetSize_ $opt(pktsize)
        $tcp set window_ $opt(rcvwin)
        $sink set window_ $opt(rcvwin)
        #Setup a FTP over TCP connection
        set ftp [new Application/FTP]
        $ftp attach-agent $tcp
        $ftp set type_ FTP
        $ns at 0.0 "$ftp start"

        # set outfile [open "congestion${i}.xg" w]
        # $ns at 0.0  "plotWindow $tcp  $outfile"

        # # Setup a UDP connection
        # set udp [new Agent/UDP]
        # $ns attach-agent $s($i) $udp
        # set null [new Agent/Null]
        # $ns attach-agent $opt(d) $null
        # $ns connect $udp $null

        # #Setup a CBR over UDP connection
        # set cbr [new Application/Traffic/CBR]
        # $cbr attach-agent $udp
        # $cbr set type_ CBR
        # $cbr set packet_size_ 1000
        # $cbr set rate_ 100Mb
        # $cbr set random_ false

        # $ns at 0.0 "$cbr start"
    }
}

create-dumbbell-topology
create-tcp-connections

$ns at $opt(simtime) "finish"

proc plotWindow {tcpSource outfile} {
   global ns
   set now [$ns now]
   set cwnd [$tcpSource set cwnd_]

# the data is recorded in a file called congestion.xg (this can be plotted # using xgraph or gnuplot. this example uses xgraph to plot the cwnd_
   puts $outfile "$now $cwnd"
   $ns at [expr $now+0.03] "plotWindow $tcpSource $outfile"
}

# proc finish {} {
#  exec xgraph congestion.xg -geometry 300x300 &
# exit 0
# }

#Run the simulation
$ns run

# TODO: Run and fix errors.

# proc create-sources-sinks {} {
#     global ns opt s d src recvapp tp protocols protosinks f linuxcc

#     set numsrc $opt(nsrc)
#     if { [string range $opt(tcp) 0 9] == "TCP/Linux/"} {
#         set linuxcc [ string range $opt(tcp) 10 [string length $opt(tcp)] ]
#         set opt(tcp) "TCP/Linux"
#     }

#     if { $opt(tcp) == "DCTCP" } {
#         Agent/TCP set dctcp_ true
#         Agent/TCP set ecn_ 1
#         Agent/TCP set old_ecn_ 1
#         Agent/TCP set packetSize_ $opt(pktsize)
#         Agent/TCP/FullTcp set segsize_ $opt(pktsize)
#         Agent/TCP set window_ 1256
#         Agent/TCP set slow_start_restart_ false
#         Agent/TCP set tcpTick_ 0.0001
#         Agent/TCP set minrto_ 0.2 ; # minRTO = 200ms
#         Agent/TCP set windowOption_ 0
#         # DCTCP uses ECN and marks based on instantaneous queue length.
#         # To get this behavior, q_weight_ for RED should be 1, mark_p 1,
#         # and the min and max thresholds should be equal.
#         # http://research.microsoft.com/en-us/um/people/padhye/publications/dctcp-sigcomm2010.pdf
#         # We use 65 because that's what the code at
#         # http://simula.stanford.edu/~alizade/Site/DCTCP.html does.
#         Queue/RED set bytes_ false
#         Queue/RED set queue_in_bytes_ true
#         Queue/RED set mean_pktsize_ $opt(pktsize)
#         Queue/RED set setbit_ true
#         Queue/RED set gentle_ false
#         Queue/RED set q_weight_ 1.0
#         Queue/RED set mark_p_ 1.0
#         Queue/RED set thresh_ 65
#         Queue/RED set maxthresh_ 65
#         DelayLink set avoidReordering_ true
#         set opt(tcp) "TCP/Newreno"
#     }

#     for {set i 0} {$i < $numsrc} {incr i} {

#         if { $opt(cycle_protocols) == true } {
#             if { [llength $protocols] < $opt(nsrc) } {
#                 puts "Need at least nsrc ($opt(nsrc)) items in protocols list. Exiting"
#                 exit 1
#             }
#             set opt(tcp) [lindex $protocols $i]
#             set opt(sink) [lindex $protosinks $i]
#             if { [string range $opt(tcp) 0 9] == "TCP/Linux/"} {
#                 set linuxcc [ string range $opt(tcp) 10 [string length $opt(tcp)] ]
#                 set opt(tcp) "TCP/Linux"
#             }
#             if { $opt(tcp) == "DCTCP" } {
#                 Agent/TCP set dctcp_ true
#                 Agent/TCP set ecn_ 1
#                 Agent/TCP set old_ecn_ 1
#                 Agent/TCP set packetSize_ $opt(pktsize)
#                 Agent/TCP/FullTcp set segsize_ $opt(pktsize)
#                 Agent/TCP set window_ 1256
#                 Agent/TCP set slow_start_restart_ false
#                 Agent/TCP set tcpTick_ 0.0001
#                 Agent/TCP set minrto_ 0.2 ; # minRTO = 200ms
#                 Agent/TCP set windowOption_ 0
#                 Queue/RED set bytes_ false
#                 Queue/RED set queue_in_bytes_ true
#                 Queue/RED set mean_pktsize_ $opt(pktsize)
#                 Queue/RED set setbit_ true
#                 Queue/RED set gentle_ false
#                 Queue/RED set q_weight_ 1.0
#                 Queue/RED set mark_p_ 1.0
#                 Queue/RED set thresh_ 65
#                 Queue/RED set maxthresh_ 65
#                 DelayLink set avoidReordering_ true
#                 set opt(tcp) "TCP/Newreno"
#             }
#         }
#         set tp($i) [$ns create-connection-list $opt(tcp) $s($i) $opt(sink) $d $i]
#         set tcpsrc [lindex $tp($i) 0]
#         set tcpsink [lindex $tp($i) 1]
#         if { [info exists linuxcc] } {
#             $ns at 0.0 "$tcpsrc select_ca $linuxcc"
#             $ns at 0.0 "$tcpsrc set_ca_default_param linux debug_level 2"
#         }

#         if { [string first "Rational" $opt(tcp)] != -1 } {
#             if { $opt(tracewhisk) == "all" || $opt(tracewhisk) == $i } {
#                 $tcpsrc set tracewhisk_ 1
#                 puts "tracing ON for connection $i: $opt(tracewhisk)"
#             } else {
#                 $tcpsrc set tracewhisk_ 0
#                 puts "tracing OFF for connection $i: $opt(tracewhisk)"
#             }
#         }
# 	$tcpsrc set fid_ [expr $i%256]
#         $tcpsrc set window_ $opt(rcvwin)
#         $tcpsrc set packetSize_ $opt(pktsize)

#         if { [info exists opt(tr)] } {
#             $tcpsrc trace cwnd_
#             $tcpsrc trace rtt_
#             $tcpsrc trace maxseq_
#             $tcpsrc trace ack_
#             if { $opt(tcp) == "TCP/Rational" } {
#                 $tcpsrc trace _intersend_time
#             }
#             $tcpsrc attach $f
#         }

#         set src($i) [ $tcpsrc attach-app $opt(app) ]
#         $src($i) setup_and_start $i $tcpsrc
#         set recvapp($i) [new LoggingApp $i]
#         $recvapp($i) attach-agent $tcpsink
#         $ns at 0.0 "$recvapp($i) start"
#     }
# }