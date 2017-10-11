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
	// RemyBuffers::WhiskerTree tree;
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
	TcpAgent::delay_bind_init_all();
	TcpAgent::reset();
	const double tickno = Scheduler::instance().clock() * 1000;
	Unicorn::reset(tickno);
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

/*
 * initial_window() is called in a few different places in tcp.cc.
 * This function overrides the default.
 */
double
UnicornTcpAgent::initial_window()
{
	const double tickno = Scheduler::instance().clock() * 1000;
	Unicorn::reset(tickno);
	update_cwnd_and_pacing();
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
	_id_to_sent_during_action[seqno] = _put_actions;
	_id_to_sent_during_flow[seqno] = _flow_id;
	_outstanding_rewards[_put_actions]["sent"] += 1;
	if (_last_send_time != 0) {
		_outstanding_rewards[_put_actions]["intersend_duration_acc"] += tickno - _last_send_time;
	}
	_packets_sent++;
	_memory.packet_sent( p );
	Unicorn::_last_send_time = tickno;

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
	packets_received(packet_for_receive);
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
	printf("%lu: cwnd_=%f, incr=%f, cwnd_=%f\n", _thread_id, (double) prev_cwnd_, ((double) cwnd_) - prev_cwnd_, (double) cwnd_);
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
