package de.dlr.sp.flatfileindexing.graphql;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import io.micronaut.http.client.annotation.Client;
import io.micronaut.test.annotation.MockBean;

import jakarta.inject.Inject;
import de.dlr.sp.flatfileindexing.model.Entity;
import de.dlr.sp.flatfileindexing.model.Activity;
import de.dlr.sp.flatfileindexing.model.Agent;
import de.dlr.sp.flatfileindexing.model.Provenance;
import graphql.ExecutionResult;
import graphql.GraphQL;
import graphql.schema.GraphQLSchema;
import graphql.schema.idl.SchemaParser;
import graphql.schema.idl.TypeDefinitionRegistry;
import graphql.schema.idl.RuntimeWiring;
import graphql.schema.idl.SchemaGenerator;
import static graphql.schema.idl.RuntimeWiring.newRuntimeWiring;

import de.dlr.sp.flatfileindexing.IProvenanceListener;
import de.dlr.sp.flatfileindexing.model.Schema;

import static org.mockito.Mockito.*;

import java.util.Arrays;
import java.util.Map;
import java.util.List;
import java.io.IOException;

@MicronautTest
public class Test_ProvenanceFetcher {

  @Inject
  ProvenanceFetcher fetcher;
  @Inject
  IProvenanceListener plist;

  @Test
  void test_get() {

    SchemaParser schemaParser = new SchemaParser();
    TypeDefinitionRegistry typeDefinitionRegistry = schemaParser.parse(Schema.SCHEMA);

    RuntimeWiring runtimeWiring = newRuntimeWiring()
      .type("Query", builder -> builder.dataFetcher("data", fetcher))
      .build();

    SchemaGenerator schemaGenerator = new SchemaGenerator();

    GraphQLSchema graphQLSchema = schemaGenerator.makeExecutableSchema(typeDefinitionRegistry, runtimeWiring);

    GraphQL build = GraphQL.newGraphQL(graphQLSchema).build();
    ExecutionResult executionResult = build.execute("{data{entity{label}}}");
    Map result = (Map)executionResult.getData();
    assertEquals(2, ((List)result.get("data")).size());

    executionResult = build.execute("{data{entity(label: \"entitylabel1\"){label}}}");
    result = (Map)executionResult.getData();
    assertEquals(1, ((List)result.get("data")).size());
  }

  @MockBean(IProvenanceListener.class)
  IProvenanceListener plistener() throws IOException {
    IProvenanceListener mocked = mock(IProvenanceListener.class);
    when(mocked.plist()).thenReturn(Arrays.asList(
          new Provenance(
            new Entity("entitylabel1", "entitytype1", "datahash1"),
            new Agent("familyname1", "givenname1", "agentlabel1", "agenttype1"),
            new Activity("start1", "end1", "activitylabel1", "location1", "means1")
          ),
          new Provenance(
            new Entity("entitylabel2", "entitytype2", "datahash2"),
            new Agent("familyname2", "givenname2", "agentlabel2", "agenttype2"),
            new Activity("start2", "end2", "activitylabel2", "location2", "means2")
          )
    ));

    return mocked;
  }
}
