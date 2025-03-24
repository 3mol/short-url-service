package com.example.shorturl.service;

public interface AsyncService {
    void runSync(Runnable runnable);
}