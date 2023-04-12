package de.dlr.sp.flatfileindexing;

import jakarta.inject.Singleton;
import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

import static java.nio.file.StandardWatchEventKinds.*;
import java.nio.file.WatchEvent;
import java.nio.file.WatchKey;
import java.nio.file.WatchService;
import java.util.stream.Collectors;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Scanner;

import io.micronaut.context.annotation.Value;
import io.micronaut.discovery.event.ServiceReadyEvent;
import io.micronaut.runtime.event.annotation.EventListener;
import io.micronaut.scheduling.annotation.Async;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import de.dlr.sp.flatfileindexing.model.Provenance;

@Singleton
public class FilewatcherService implements IProvenanceListener {
  @Value("${flatfileindexing.watchdir}")
  protected String watchdir;

  private final List<Provenance> plist;

  private Logger logger = LoggerFactory.getLogger("flatfileindexing");
  private WatchService wserv;

  public FilewatcherService() throws IOException {
    this.wserv = FileSystems.getDefault().newWatchService();
    this.plist = new ArrayList<>();
  }

  public final List<Provenance> plist() {
    return Collections.unmodifiableList(this.plist);
  }

  private void scanAndSetup() {
    Path p = Paths.get(this.watchdir);
    try {
      p.register(this.wserv, ENTRY_CREATE, ENTRY_MODIFY);
      Files.walk(p).filter(Files::isDirectory).forEach(d -> {
        try{
          d.register(this.wserv, ENTRY_CREATE, ENTRY_MODIFY);
        }
        catch(IOException e) {
          this.logger.error("Error registering watcher for: %s".formatted(this.watchdir));
        }
      });

      List<Path> provpaths = Files.walk(p).filter(Files::isRegularFile).filter(f -> f.getFileName().toString().endsWith(".prov")).collect(Collectors.toList());
      for(Path pp : provpaths) {
        try(Scanner scanner =new Scanner(pp.toFile())) {
          scanner.useDelimiter("\\Z");
          String provstring = scanner.next();
          Provenance prov = new JSONDeserializer().deserialize(provstring);
          this.plist.add(prov);
        }
        catch(IOException e) {
          this.logger.error("Error reading file %s".formatted(pp.getFileName()), e);
        }
      }
    }
    catch(IOException e) {
      this.logger.error("Error while scanning directory: %s".formatted(this.watchdir), e);
    }
  }

  @EventListener
  public void run(ServiceReadyEvent evt) {
    this.logger.info("Watching directory: %s".formatted(this.watchdir));
    this.scanAndSetup();
    this.listen();
  }

  @Async
  void listen() {
    try {
      for(;;) {
        WatchKey key = wserv.take();
        for (WatchEvent<?> event: key.pollEvents()) {

        }
        key.reset();
      }
    }
    catch(InterruptedException e) {
      this.logger.error("Exception while watching directory", e);
    }
    this.logger.info(String.format("Watching %s", this.watchdir));
  }
}
