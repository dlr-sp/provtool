package de.dlr.sp.flatfileindexing;

import io.micronaut.http.HttpResponse;
import io.micronaut.http.HttpStatus;
import io.micronaut.http.MediaType;
import io.micronaut.http.annotation.Body;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import jakarta.annotation.PostConstruct;
import jakarta.inject.Inject;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import graphql.ExecutionResult;
import graphql.GraphQL;
import graphql.schema.GraphQLSchema;
import graphql.schema.idl.RuntimeWiring;
import graphql.schema.idl.SchemaGenerator;
import graphql.schema.idl.SchemaParser;
import graphql.schema.idl.TypeDefinitionRegistry;

import static graphql.schema.idl.RuntimeWiring.newRuntimeWiring;

import de.dlr.sp.flatfileindexing.graphql.ProvenanceFetcher;
import de.dlr.sp.flatfileindexing.model.Schema;

import java.util.Map;

import org.json.simple.JSONValue;

@Controller("/search")
public class Searchnode {

  @Inject
  ProvenanceFetcher fetcher;

  private Logger logger = LoggerFactory.getLogger("flatfileindexing");

  private GraphQL graphql;

  public Searchnode() {
  }

  @PostConstruct
  public void init() {

    SchemaParser schemaParser = new SchemaParser();
    TypeDefinitionRegistry typeDefinitionRegistry = schemaParser.parse(Schema.SCHEMA);

    RuntimeWiring runtimeWiring = newRuntimeWiring()
      .type("Query", builder -> builder.dataFetcher("data", fetcher))
      .build();

    SchemaGenerator schemaGenerator = new SchemaGenerator();
    GraphQLSchema graphQLSchema = schemaGenerator.makeExecutableSchema(typeDefinitionRegistry, runtimeWiring);

    this.graphql = GraphQL.newGraphQL(graphQLSchema).build();
  }

  @Post(produces = MediaType.APPLICATION_JSON)
  public HttpResponse query(@Body String search) {
    ExecutionResult executionResult = this.graphql.execute(search);
    if(executionResult.getErrors().size() > 0) {
      this.logger.error(executionResult.getErrors().toString());
    }

    try {
      Map<String, Object> toSpecificationResult = executionResult.toSpecification();
      return HttpResponse.ok().body(JSONValue.toJSONString(toSpecificationResult.get("data")));
    }
    catch(Exception e) {
      this.logger.error("Query could not be performed", e);
      return HttpResponse.status(HttpStatus.BAD_REQUEST, "Query could not be performed. Is the query syntax correct?");
    }
  }
}
