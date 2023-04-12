package de.dlr.sp.flatfileindexing.model;

public final class Schema {
  public static final String SCHEMA = 
      "type Query {" +
      "  data: [Provenance]" +
      "}" +
      "type Provenance {" +
      "  entity(label: String): Entity" +
      "}" +
      "type Entity {" +
      "  datahash: String" +
      "  label: String" +
      "  type: String" +
      "}";
}
