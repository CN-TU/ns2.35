/* -*-	Mode:C++; c-basic-offset:8; tab-width:8; indent-tabs-mode:t -*- */
/*
 * Super-rational TCP congestion control.
 * Keith Winstein, Hari Balakrishnan (MIT CSAIL & Wireless@MIT).
 * January 2013.
 */

#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <assert.h>
#include <iostream>

#include "tcp-unicorn.h"

// FIXME: Don't hardcode cooperative and delay delta
UnicornTcpAgent::UnicornTcpAgent() : Unicorn(true)
{
	bind_bool("count_bytes_acked_", &count_bytes_acked_);
	_training = false;
	// FIXME: I guess that this means that the maximum burst length is disabled?
	maxburst_ = 0;
	/* get whisker filename */
	// const char *filename = getenv( "WHISKERS" );
	// if ( !filename ) {
	// 	fprintf( stderr, "RemyTCP: Missing WHISKERS environment variable.\n" );
	// 	throw 1;
	// }

	// /* open file */
	// int fd = open( filename, O_RDONLY );
	// if ( fd < 0 ) {
	// 	perror( "open" );
	// 	throw 1;
	// }

	// /* parse whisker definition */
	// RemyRemyBuffers::WhiskerTree tree;
	// if ( !tree.ParseFromFileDescriptor( fd ) ) {
	// 	fprintf( stderr, "RemyTCP: Could not parse whiskers in \"%s\".\n", filename );
	// 	throw 1;
	// }

	// /* close file */
	// if ( ::close( fd ) < 0 ) {
	// 	perror( "close" );
	// 	throw 1;
	// }

	/* store whiskers */
	// _whiskers = new WhiskerTree( tree );
	// _unicorn = new Unicorn(false);
}

UnicornTcpAgent::~UnicornTcpAgent() {}

void
UnicornTcpAgent::delay_bind_init_all() {
	printf("%lu: In delay bind init all\n", _thread_id);
	TcpAgent::delay_bind_init_all();
	TcpAgent::reset();
	const double tickno = Scheduler::instance().clock() * 1000;
	Unicorn::reset(tickno);
	cwnd_ = _the_window;
}

int
UnicornTcpAgent::delay_bind_dispatch(const char *varName, const char *localName, TclObject *tracer) {
  return TcpAgent::delay_bind_dispatch(varName, localName, tracer);
}


static class UnicornTcpClass : public TclClass {
public:
	UnicornTcpClass() : TclClass("Agent/TCP/Unicorn") {}
	TclObject* create(int, const char*const*) {
		return (new UnicornTcpAgent());
	}
} class_unicorn_tcp;

static class UnicornRenoTcpClass : public TclClass {
public:
	UnicornRenoTcpClass() : TclClass("Agent/TCP/Reno/Unicorn") {}
	TclObject* create(int, const char*const*) {
		return (new UnicornRenoTcpAgent());
	}
} class_unicorn_reno_tcp;

static class UnicornNewRenoTcpClass : public TclClass {
public:
	UnicornNewRenoTcpClass() : TclClass("Agent/TCP/Newreno/Unicorn") {}
	TclObject* create(int, const char*const*) {
		return (new UnicornNewRenoTcpAgent());
	}
} class_unicorn_newreno_tcp;

// void
// UnicornTcpAgent::slowdown(int how)
// {
// 	// puts("Calling freaking slowdown in tcp-unicorn");
// 	double decrease;  /* added for highspeed - sylvia */
// 	double win, halfwin, decreasewin;
// 	int slowstart = 0;
// 	++ncwndcuts_;
// 	if (!(how & TCP_IDLE) && !(how & NO_OUTSTANDING_DATA)){
// 		++ncwndcuts1_;
// 	}
// 	// we are in slowstart for sure if cwnd < ssthresh
// 	if (cwnd_ < ssthresh_)
// 		slowstart = 1;
//         if (precision_reduce_) {
// 		halfwin = windowd() / 2;
//                 if (wnd_option_ == 6) {
//                         /* binomial controls */
//                         decreasewin = windowd() - (1.0-decrease_num_)*pow(windowd(),l_parameter_);
//                 } else if (wnd_option_ == 8 && (cwnd_ > low_window_)) {
//                         /* experimental highspeed TCP */
// 			decrease = decrease_param();
// 			//if (decrease < 0.1)
// 			//	decrease = 0.1;
// 			decrease_num_ = decrease;
//                         decreasewin = windowd() - (decrease * windowd());
//                 } else {
// 	 		decreasewin = decrease_num_ * windowd();
// 		}
// 		win = windowd();
// 	} else  {
// 		int temp;
// 		temp = (int)(window() / 2);
// 		halfwin = (double) temp;
//                 if (wnd_option_ == 6) {
//                         /* binomial controls */
//                         temp = (int)(window() - (1.0-decrease_num_)*pow(window(),l_parameter_));
//                 } else if ((wnd_option_ == 8) && (cwnd_ > low_window_)) {
//                         /* experimental highspeed TCP */
// 			decrease = decrease_param();
// 			//if (decrease < 0.1)
//                         //       decrease = 0.1;
// 			decrease_num_ = decrease;
//                         temp = (int)(windowd() - (decrease * windowd()));
//                 } else {
//  			temp = (int)(decrease_num_ * window());
// 		}
// 		decreasewin = (double) temp;
// 		win = (double) window();
// 	}
// 	if (how & CLOSE_SSTHRESH_HALF)
// 		// For the first decrease, decrease by half
// 		// even for non-standard values of decrease_num_.
// 		if (first_decrease_ == 1 || slowstart ||
// 			last_cwnd_action_ == CWND_ACTION_TIMEOUT) {
// 			// Do we really want halfwin instead of decreasewin
// 		// after a timeout?
// 			ssthresh_ = (int) halfwin;
// 		} else {
// 			ssthresh_ = (int) decreasewin;
// 		}
// 	else if (how & CLOSE_SSTHRESH_DCTCP)
// 		ssthresh_ = (int) ((1 - dctcp_alpha_/2.0) * windowd());
//         else if (how & THREE_QUARTER_SSTHRESH)
// 		if (ssthresh_ < 3*cwnd_/4)
// 			ssthresh_  = (int)(3*cwnd_/4);
// 	if (how & CLOSE_CWND_HALF)
// 		// For the first decrease, decrease by half
// 		// even for non-standard values of decrease_num_.
// 		if (first_decrease_ == 1 || slowstart || decrease_num_ == 0.5) {
// 			cwnd_ = halfwin;
// 		} else cwnd_ = decreasewin;
// 	else if (how & CLOSE_CWND_DCTCP)
// 		cwnd_ = (1 - dctcp_alpha_/2.0) * windowd();
//         else if (how & CWND_HALF_WITH_MIN) {
// 		// We have not thought about how non-standard TCPs, with
// 		// non-standard values of decrease_num_, should respond
// 		// after quiescent periods.
//                 cwnd_ = decreasewin;
// 								if (cwnd_ < 1) {
// 												puts("cwnd_ 2");
// 												cwnd_ = initial_window();
// 								}
// 	}
// 	else if (how & CLOSE_CWND_RESTART)
// 		cwnd_ = int(wnd_restart_);
// 	else if (how & CLOSE_CWND_INIT)
// 		cwnd_ = int(wnd_init_);
// 	else if (how & CLOSE_CWND_ONE) {
// 		// puts("cwnd_ 3");
// 		// FIXME: WTF is the window randomly set to 1 all the time and not to `initial_window()'?
// 		cwnd_ = initial_window();
// 	} else if (how & CLOSE_CWND_HALF_WAY) {
// 		// cwnd_ = win - (win - W_used)/2 ;
// 		cwnd_ = W_used + decrease_num_ * (win - W_used);
//                 if (cwnd_ < 1) {
// 												puts("cwnd_ 4");
// 												cwnd_ = initial_window();
// 								}
// 	}
// 	if (ssthresh_ < 2)
// 		ssthresh_ = 2;
// 	if (cwnd_ < 1) {
// 		puts("cwnd_ 5");
// 		cwnd_ = initial_window();
// 	}
// 		if (how & (CLOSE_CWND_HALF|CLOSE_CWND_RESTART|CLOSE_CWND_INIT|CLOSE_CWND_ONE|CLOSE_CWND_DCTCP))
// 		cong_action_ = TRUE;

// 	fcnt_ = count_ = 0;
// 	if (first_decrease_ == 1)
// 		first_decrease_ = 0;
// 	// for event tracing slow start
// 	if (cwnd_ == 1 || slowstart)
// 		// Not sure if this is best way to capture slow_start
// 		// This is probably tracing a superset of slowdowns of
// 		// which all may not be slow_start's --Padma, 07/'01.
// 		trace_event("SLOW_START");
// }

// void
// UnicornTcpAgent::set_initial_window()
// {
// 	// printf("%lu: In set initial window\n", _thread_id);
// 	if (syn_ && delay_growth_) {
// 		syn_connects_ = 0;
// 	}
// 	puts("cwnd_ in 1");
// 	cwnd_ = initial_window();
// }

/*
 * initial_window() is called in a few different places in tcp.cc.
 * This function overrides the default.
 */
double
UnicornTcpAgent::initial_window()
{
	const double tickno = Scheduler::instance().clock() * 1000;
	// printf("%lu: In initial window at %f\n", _thread_id, tickno);
	Unicorn::reset(tickno);
	UnicornTcpAgent::update_cwnd_and_pacing();
	return cwnd_;
}

void
UnicornTcpAgent::send_helper(int maxburst)
{
	/*
	 * If there is still data to be sent and there is space in the
	 * window, set a timer to schedule the next burst. Note that
	 * we wouldn't get here if TCP_TIMER_BURSTSEND were pending,
	 * so we do not need an explicit check here.
	 */

	/* schedule wakeup */
	// FIXME: I suppose that this can never happen?
	if ( t_seqno_ <= highest_ack_ + window() && t_seqno_ < curseq_ ) {
		// const double now( Scheduler::instance().clock() );
		// const double time_since_last_send( now - _last_send_time );
		// const double wait_time( _intersend_time - time_since_last_send );
		// if ( wait_time <= 0 ) {
			burstsnd_timer_.resched( 0 );
		// } else {
			// burstsnd_timer_.resched( wait_time );
		// }
	}
}

void UnicornTcpAgent::output( int seqno, int reason ) {
	const double tickno = Scheduler::instance().clock() * 1000;

	remy::Packet p( 0, 0, tickno, seqno );
	_id_to_sent_during_flow[_packets_sent] = _flow_id;

	if (_last_send_time == 0) {
		_memory._last_tick_sent = tickno;
		_memory._last_tick_received = tickno;
		_flow_to_last_received[_flow_id] = tickno;
	}

	_last_send_time = tickno;
	_id_to_sent_during_action[_packets_sent] = _put_actions;
	_outstanding_rewards[_put_actions]["sent"] += 1;
	_outstanding_rewards[_put_actions]["intersend_duration_acc"] += tickno - _last_send_time;
	_packets_sent++;

	_memory.packet_sent( p );

	TcpAgent::output( seqno, reason );
}

/*
 * Connection has been idle for some time.
 */
void
UnicornTcpAgent::send_idle_helper()
{
	const double now( Scheduler::instance().clock() );

	if ( now - _last_send_time > 0.2 ) {
		/* timeout */
		// printf("%lu: Calling send idle_helper...\n", _thread_id);
		initial_window();
	}

	/* we want to pace each packet */
	// maxburst_ = 1;

	// const double time_since_last_send( now - _last_send_time );
	// const double wait_time( _intersend_time - time_since_last_send );

	// if ( wait_time <= .0001 ) {
	// 	return;
	// } else {
	// 	burstsnd_timer_.resched( wait_time );
	// }
}

/*
 * recv_newack_helper(pkt) is called from TcpAgent::recv() in tcp.cc when a
 * new cumulative ACK arrives.
 * Process a new ACK: update SRTT, make sure to call newack() of the parent
 * class, and, most importantly, update cwnd according to the model.
 * This function overrides the default.
 */
void
UnicornTcpAgent::recv_newack_helper(Packet *pkt)
{
	double now = Scheduler::instance().clock();
	hdr_tcp *tcph = hdr_tcp::access(pkt);
	double last_rtt = Scheduler::instance().clock() - tcph->ts_echo();
	double g = 1/8; /* gain used for smoothing rtt */
	double h = 1/4; /* gain used for smoothing rttvar */
	double delta;
	int ackcount, i;

	double last_ack_time_ = now;
	/*
	 * If we are counting the actual amount of data acked, ackcount >= 1.
	 * Otherwise, ackcount=1 just as in standard TCP.
	 */
	if (count_bytes_acked_) {
		ackcount = tcph->seqno() - last_ack_;
	} else {
		ackcount = 1;
	}
	newack(pkt);		// updates RTT to set RTO properly, etc.
	maxseq_ = ::max(maxseq_, highest_ack_);
	update_memory( remy::Packet( tcph->seqno(), 1000 * tcph->ts_echo(), 1000 * now ) );
	update_cwnd_and_pacing();
	/* if the connection is done, call finish() */
	if ((highest_ack_ >= curseq_-1) && !closed_) {
		closed_ = 1;
		finish();
	}
}

void
UnicornTcpAgent::update_memory(const remy::Packet packet)
{
	std::vector<remy::Packet> packet_for_receive;
	packet_for_receive.push_back(packet);
	// This is necessary when tcp.cc suddenly resets the window to 1 without calling `initial_window()'
	Unicorn::_the_window = TcpAgent::cwnd_;
	Unicorn::packets_received(packet_for_receive);
}

void
UnicornTcpAgent::update_cwnd_and_pacing( void )
{
	// const Whisker & current_whisker( _whiskers->use_whisker( _memory ) );
	// unsigned int new_cwnd = current_whisker.window( (unsigned int)cwnd_ );
	// if ( new_cwnd > 1024 ) {
	// 	new_cwnd = 1024;
	// }

	// printf("%lu: before update in tcp-unicorn: cwnd_=%f, _the_window=%f\n", _thread_id, (double) cwnd_, _the_window);
	const double prev_cwnd_ = (double) cwnd_;
	cwnd_ = Unicorn::_the_window;
	// printf("%lu: cwnd_=%f, incr=%f, cwnd_=%f\n", _thread_id, (double) prev_cwnd_, ((double) cwnd_) - prev_cwnd_, (double) cwnd_);
	// _intersend_time = .001 * current_whisker.intersend();
	// if (trace_) {
	// 	fprintf( stderr, "memory: %s falls into whisker %s\n", _memory.str().c_str(), current_whisker.str().c_str() );
	// 	fprintf( stderr, "\t=> cwnd now %u, intersend_time now %f\n", new_cwnd, _intersend_time );
	// }

	//	fprintf( stderr, "cwnd now %u, intersend_time now %f\n", new_cwnd, _intersend_time );
}

void
UnicornTcpAgent::timeout_nonrtx( int tno )
{
	if ( tno == TCP_TIMER_DELSND ) {
		send_much( 1, TCP_REASON_TIMEOUT, maxburst_ );
	} else if ( tno == TCP_TIMER_BURSTSND ) {
		send_much( 1, TCP_REASON_TIMEOUT, maxburst_ );
	}
}
