#ifndef WHISKERTREE_HH
#define WHISKERTREE_HH

#include "whisker.hh"
#include "memoryrange.hh"
#include "remydna.pb.h"

class WhiskerTree {
private:
  MemoryRange _domain;

  std::vector< WhiskerTree > _children;
  std::vector< Whisker > _leaf;

  const Whisker * whisker( const RemyMemory & _memory ) const;

public:
  const Whisker & use_whisker( const RemyMemory & _memory ) const;

  bool is_leaf( void ) const;

  WhiskerTree( const RemyRemyBuffers::WhiskerTree & dna );
};

#endif
