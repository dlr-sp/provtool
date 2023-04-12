package de.dlr.sp.flatfileindexing;

import org.junit.jupiter.api.Test;

import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import io.micronaut.test.annotation.MockBean;

import de.dlr.sp.flatfileindexing.model.Entity;
import de.dlr.sp.flatfileindexing.model.Activity;
import de.dlr.sp.flatfileindexing.model.Agent;
import de.dlr.sp.flatfileindexing.model.Provenance;

import static org.mockito.Mockito.*;

import io.restassured.specification.RequestSpecification;
import static org.hamcrest.Matchers.hasSize;

import java.util.Arrays;
import java.io.IOException;

@MicronautTest
public class Test_Searchnode{

  @Test
  void test_query(RequestSpecification spec) {
    spec.header("Content-type", "application/json").
      and().body("{data{entity{label}}}").
      when().post("/search").
      then().statusCode(200).body("data", hasSize(2));
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
