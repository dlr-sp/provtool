package de.dlr.sp.flatfileindexing;

import io.micronaut.runtime.Micronaut;

public class Application {
    public static void main(String[] args) throws InterruptedException {
        Micronaut.build(args).mainClass(Application.class).start();
    }
}
