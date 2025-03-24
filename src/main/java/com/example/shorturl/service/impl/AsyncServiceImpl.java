package com.example.shorturl.service.impl;

import com.example.shorturl.service.AsyncService;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;

@Component
public class AsyncServiceImpl implements AsyncService {

    @Async
    @Override
    public void runSync(Runnable runnable) {
        runnable.run();
    }
}