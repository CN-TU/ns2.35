/* -*-	Mode:C++; c-basic-offset:8; tab-width:8; indent-tabs-mode:t -*- */
/*
 * Super-rational TCP congestion control.
 * Keith Winstein, Hari Balakrishnan (MIT CSAIL & Wireless@MIT).
 * January 2013.
 */

#ifndef ns_tcp_unicorn_h
#define ns_tcp_unicorn_h

#include "tcp.h"
#include "ip.h"
#include "flags.h"
#include "random.h"
#include "template.h"

#include "unicorn/src/unicorn.hh"

/* Unicorn TCP with Tahoe */
class UnicornTcpAgent : public virtual TcpAgent, public Unicorn {
public:
	UnicornTcpAgent();
	~UnicornTcpAgent();

	/* helper functions */
	virtual void send_helper(int maxburst);
	virtual void send_idle_helper();
	virtual void recv_newack_helper(Packet* pkt);
	virtual double initial_window();
	virtual void update_memory( const remy::Packet packet );
	virtual void timeout_nonrtx( int tno );
	virtual void output( int seqno, int reason );
	virtual void update_cwnd_and_pacing( void );

protected:
	virtual void delay_bind_init_all();
	virtual int delay_bind_dispatch(const char *varName, const char *localName, TclObject *tracer);
	int count_bytes_acked_;
};

/*
 * Unicorn TCP with Reno.
 */

class UnicornRenoTcpAgent : public virtual RenoTcpAgent, public UnicornTcpAgent {
public:
	UnicornRenoTcpAgent() : RenoTcpAgent(), UnicornTcpAgent() {}

	/* helper functions */
	virtual void send_helper(int maxburst) {UnicornTcpAgent::send_helper(maxburst);}
	virtual void send_idle_helper() {UnicornTcpAgent::send_idle_helper();}
	virtual void recv_newack_helper(Packet* pkt) {UnicornTcpAgent::recv_newack_helper(pkt);}
	virtual double initial_window() {return UnicornTcpAgent::initial_window();}
	virtual void update_memory( const remy::Packet packet ) {UnicornTcpAgent::update_memory(packet);}
	virtual void output( int seqno, int reason )  {UnicornTcpAgent::output( seqno, reason );}
};

/*
 * Unicorn TCP with NewReno.
 */
class UnicornNewRenoTcpAgent : public virtual NewRenoTcpAgent, public UnicornTcpAgent {
public:
	UnicornNewRenoTcpAgent() : NewRenoTcpAgent(), UnicornTcpAgent() {}

	/* helper functions */
	virtual void send_helper(int maxburst) {UnicornTcpAgent::send_helper(maxburst);}
	virtual void send_idle_helper() {UnicornTcpAgent::send_idle_helper();}
	virtual void recv_newack_helper(Packet* pkt) {UnicornTcpAgent::recv_newack_helper(pkt);}
	virtual double initial_window() {return UnicornTcpAgent::initial_window();}
	virtual void update_memory( const remy::Packet packet ) {UnicornTcpAgent::update_memory(packet);}
	virtual void output( int seqno, int reason )  {UnicornTcpAgent::output( seqno, reason );}
};

#endif
