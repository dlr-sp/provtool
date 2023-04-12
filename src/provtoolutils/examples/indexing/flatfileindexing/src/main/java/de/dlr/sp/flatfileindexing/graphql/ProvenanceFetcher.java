package de.dlr.sp.flatfileindexing.graphql;

import graphql.schema.DataFetcher;
import graphql.schema.DataFetchingEnvironment;
import graphql.schema.SelectedField;

import java.util.List;
import java.util.stream.Collectors;

import jakarta.inject.Inject;
import jakarta.inject.Singleton;

import de.dlr.sp.flatfileindexing.IProvenanceListener;
import de.dlr.sp.flatfileindexing.model.Provenance;

@Singleton
public class ProvenanceFetcher implements DataFetcher<List<Provenance>> {
  @Inject
  IProvenanceListener watcher;

  @Override
  public List<Provenance> get(DataFetchingEnvironment env) {
    List<SelectedField> sel = env.getSelectionSet().getFields("entity");
    String lab = (String)sel.stream().findFirst().get().getArguments().getOrDefault("label", "");

    return watcher.plist().stream().filter(p -> {
      if(lab.length() > 0) {
        return p.entity().label().equalsIgnoreCase(lab);
      }
      return true;
    }).collect(Collectors.toList());
  }
}
