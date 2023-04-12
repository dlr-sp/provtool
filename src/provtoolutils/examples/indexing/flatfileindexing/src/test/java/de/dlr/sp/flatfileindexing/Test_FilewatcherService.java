package de.dlr.sp.flatfileindexing;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

import io.micronaut.test.extensions.junit5.annotation.MicronautTest;

import jakarta.inject.Inject;

import java.util.List;

import de.dlr.sp.flatfileindexing.model.Provenance;

@MicronautTest
public class Test_FilewatcherService {

  @Inject
  FilewatcherService watcher;

  @Test
  void test_staticinit() {
    List<Provenance> plist =  this.watcher.plist();
    assertEquals(2, plist.size());
  }
}
