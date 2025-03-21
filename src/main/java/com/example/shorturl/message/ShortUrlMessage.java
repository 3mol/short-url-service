package com.example.shorturl.message;

public class ShortUrlMessage {
    private String shortUrl;
    private String originalUrl;

    public ShortUrlMessage() {
    }

    public ShortUrlMessage(String shortUrl, String originalUrl) {
        this.shortUrl = shortUrl;
        this.originalUrl = originalUrl;
    }

    public String getShortUrl() {
        return shortUrl;
    }

    public void setShortUrl(String shortUrl) {
        this.shortUrl = shortUrl;
    }

    public String getOriginalUrl() {
        return originalUrl;
    }

    public void setOriginalUrl(String originalUrl) {
        this.originalUrl = originalUrl;
    }

    @Override
    public String toString() {
        return "ShortUrlMessage{" +
                "shortUrl='" + shortUrl + '\'' +
                ", originalUrl='" + originalUrl + '\'' +
                '}';
    }
} 