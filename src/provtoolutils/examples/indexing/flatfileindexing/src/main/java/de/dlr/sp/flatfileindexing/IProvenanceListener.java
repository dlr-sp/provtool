package de.dlr.sp.flatfileindexing;

import de.dlr.sp.flatfileindexing.model.Provenance;

import java.util.List;

public interface IProvenanceListener {
  public List<Provenance> plist();
}
