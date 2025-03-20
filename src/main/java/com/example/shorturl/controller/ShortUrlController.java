package com.example.shorturl.controller;

import com.example.shorturl.entity.ShortUrl;
import com.example.shorturl.service.ShortUrlService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Optional;

@RestController
@RequestMapping("/short-url")
public class ShortUrlController {
    private final ShortUrlService shortUrlService;

    @Autowired
    public ShortUrlController(ShortUrlService shortUrlService) {
        this.shortUrlService = shortUrlService;
    }

    @GetMapping
    public ResponseEntity<String> get(@RequestParam String shortUrl) {
        Optional<String> originalUrl = shortUrlService.getOriginalUrl(shortUrl);
        return originalUrl
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/info")
    public ResponseEntity<ShortUrl> getInfo(@RequestParam String shortUrl) {
        Optional<ShortUrl> shortUrlInfo = shortUrlService.getShortUrlInfo(shortUrl);
        return shortUrlInfo
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<String> add(@RequestParam String url) {
        String shortUrl = shortUrlService.createShortUrl(url);
        return ResponseEntity.status(HttpStatus.CREATED).body(shortUrl);
    }
}