package de.dlr.sp.flatfileindexing;

import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import de.dlr.sp.flatfileindexing.model.Activity;
import de.dlr.sp.flatfileindexing.model.Agent;
import de.dlr.sp.flatfileindexing.model.Entity;
import de.dlr.sp.flatfileindexing.model.Provenance;

public class JSONDeserializer {

  private Logger logger = LoggerFactory.getLogger("flatfileindexing");

  public final Provenance deserialize(String provstring) {
    JSONParser parser = new JSONParser();
    try {
      Map jobj = (Map) parser.parse(provstring);
      Map self = (Map)jobj.get("entity");
      Map ent = (Map)self.get("self");

      Map agents = (Map)jobj.get("agent");
      Map agent = (Map)agents.get(agents.keySet().stream().findFirst().get());
      Map activities = (Map)jobj.get("activity");
      Map activity = (Map)activities.get(activities.keySet().stream().findFirst().get());

      return new Provenance(new Entity(
            (String)ent.get("prov:label"),
            (String)ent.get("prov:type"),
            (String)ent.get("provtool:datahash")
        ), new Agent(
            (String)agent.get("person:familyName"),
            (String)agent.get("person:givenName"),
            (String)agent.get("prov:label"),
            (String)agent.get("prov:type")
        ),
        new Activity(
            (String)activity.get("prov:startTime"),
            (String)activity.get("prov:endTime"),
            (String)activity.get("prov:label"),
            (String)activity.get("prov:location"),
            (String)activity.get("provtool:means")
          ));
    }
    catch(ParseException e) {
      this.logger.error("Error while parsing provenance string", e);
      return new Provenance(null, null, null);
    }
  }
}
