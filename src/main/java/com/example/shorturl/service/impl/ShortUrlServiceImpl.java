package com.example.shorturl.service.impl;

import com.example.shorturl.entity.ShortUrl;
import com.example.shorturl.repository.ShortUrlRepository;
import com.example.shorturl.service.ShortUrlService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;
import java.util.UUID;

@Service
public class ShortUrlServiceImpl implements ShortUrlService {

    private final ShortUrlRepository shortUrlRepository;

    @Autowired
    public ShortUrlServiceImpl(ShortUrlRepository shortUrlRepository) {
        this.shortUrlRepository = shortUrlRepository;
    }

    @Override
    @Transactional
    public String createShortUrl(String originalUrl) {
        // 检查URL是否已存在
        Optional<ShortUrl> existingUrl = shortUrlRepository.findByOriginalUrl(originalUrl);
        if (existingUrl.isPresent()) {
            return existingUrl.get().getShortUrl();
        }

        // 生成短链接
        String shortUrl = generateShortUrl();
        
        // 确保短链接唯一
        while (shortUrlRepository.findByShortUrl(shortUrl).isPresent()) {
            shortUrl = generateShortUrl();
        }

        // 创建并保存短链接
        ShortUrl urlEntity = new ShortUrl(shortUrl, originalUrl);
        shortUrlRepository.save(urlEntity);
        
        return shortUrl;
    }

    @Override
    public Optional<String> getOriginalUrl(String shortUrl) {
        return shortUrlRepository.findByShortUrl(shortUrl)
                .map(ShortUrl::getOriginalUrl);
    }

    @Override
    public Optional<ShortUrl> getShortUrlInfo(String shortUrl) {
        return shortUrlRepository.findByShortUrl(shortUrl);
    }

    /**
     * 生成短链接
     * @return 生成的短链接
     */
    private String generateShortUrl() {
        // 使用UUID生成随机字符串并截取前8位
        return UUID.randomUUID().toString().replace("-", "").substring(0, 8);
    }
} 