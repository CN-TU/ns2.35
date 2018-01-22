#ifndef MEMORYRANGE_HH
#define MEMORYRANGE_HH

#include <string>

#include "memory.hh"
#include "remydna.pb.h"

class MemoryRange {
private:
  RemyMemory _lower, _upper;

public:
  MemoryRange( const RemyMemory & s_lower, const RemyMemory & s_upper )
    : _lower( s_lower ), _upper( s_upper )
  {}

  bool contains( const RemyMemory & query ) const;

  bool operator==( const MemoryRange & other ) const;

  MemoryRange( const RemyRemyBuffers::MemoryRange & dna );

  std::string str( void ) const;
};

#endif
