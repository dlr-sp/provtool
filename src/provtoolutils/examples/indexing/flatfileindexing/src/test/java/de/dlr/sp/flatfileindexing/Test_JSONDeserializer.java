package de.dlr.sp.flatfileindexing;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import org.junit.jupiter.api.Test;

import de.dlr.sp.flatfileindexing.model.Provenance;

public class Test_JSONDeserializer {

  @Test
  void test_deserialize() {
    String teststring = "{" +
      "\"entity\": {" +
        "\"self\": {" +
          "\"creative:encodingFormat\": \"text/plain\"," +
          "\"prov:label\": \"testfile1.txt\"," +
          "\"prov:type\": \"File\"," +
          "\"provtool:datahash\": \"66a045b452102c59d840ec097d59d9467e13a3f34f6494e539ffd32c1bb35f18\"" +
        "}" +
      "}," +  
      "\"agent\": {" +
        "\"7a6196ebb0a1ea5c28573de1c351b2b00940e732dd17893f2702d1c2d53510a9\": {" +
          "\"person:familyName\": \"Dressel\"," +
          "\"person:givenName\": \"Frank\"," +
          "\"prov:label\": \"Frank Dressel\"," +
          "\"prov:type\": \"prov:Person\"" +
        "}" +
      "}," +
      "\"activity\": {" +
        "\"a8f8b9077198f9d5fe45ccd63193c0341b5b5b7b7fad179a3d0715f5be646d67\": {" +
          "\"prov:endTime\": \"2021-07-23T14:43:00+00:00\"," +
          "\"prov:label\": \"Creation of test file\"," +
          "\"prov:location\": \"sp-000093u\"," +
          "\"prov:startTime\": \"2021-07-23T14:43:00+00:00\"," +
          "\"provtool:means\": \"-\"" +
        "}" +
      "}" +
    "}";

    Provenance prov = new JSONDeserializer().deserialize(teststring);

    assertNotNull(prov.entity());
    assertEquals("testfile1.txt", prov.entity().label());
    assertEquals("File", prov.entity().type());
    assertEquals("66a045b452102c59d840ec097d59d9467e13a3f34f6494e539ffd32c1bb35f18", prov.entity().datahash());

    assertNotNull(prov.agent());
    assertEquals("Dressel", prov.agent().familyname());
    assertEquals("Frank", prov.agent().givenname());
    assertEquals("Frank Dressel", prov.agent().label());
    assertEquals("prov:Person", prov.agent().type());

    assertNotNull(prov.activity());
    assertEquals("2021-07-23T14:43:00+00:00", prov.activity().starttime());
    assertEquals("2021-07-23T14:43:00+00:00", prov.activity().endtime());
    assertEquals("-", prov.activity().means());

    prov = new JSONDeserializer().deserialize("");
    assertNotNull(prov);
    assertNull(prov.entity());
    assertNull(prov.activity());
    assertNull(prov.agent());
  }
}
