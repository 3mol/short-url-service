package com.example.shorturl.service.impl;

import com.example.shorturl.entity.ShortUrl;
import com.example.shorturl.message.ShortUrlMessage;
import com.example.shorturl.repository.ShortUrlRepository;
import com.example.shorturl.service.KafkaProducerService;
import com.example.shorturl.service.ShortUrlService;
import jakarta.annotation.Resource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;
import java.util.concurrent.TimeUnit;

@Service
public class ShortUrlServiceImpl implements ShortUrlService {

    @Resource
    private ShortUrlRepository shortUrlRepository;

    @Resource
    private RedisTemplate<String, String> redisTemplate;

    @Resource
    KafkaProducerService kafkaProducerService;

    private static final String REDIS_KEY_PREFIX = "short_url:";
    private static final long REDIS_EXPIRE_TIME = 1;
    private static final TimeUnit REDIS_EXPIRE_UNIT = TimeUnit.MINUTES;

    @Override
    public String createShortUrl(String originalUrl) {
        // 检查URL是否已存在
        Optional<ShortUrl> existingUrl = shortUrlRepository.findByOriginalUrl(originalUrl);
        if (existingUrl.isPresent()) {
            return existingUrl.get().getShortUrl();
        }

        // 生成短链接
        ShortUrl shortUrl = new ShortUrl();
        shortUrl.setOriginalUrl(originalUrl);
        shortUrl.setShortUrl(generateShortCode());
        // 保存到Redis
        String redisKey = REDIS_KEY_PREFIX + shortUrl.getShortUrl();
        redisTemplate.opsForValue().set(redisKey, originalUrl, REDIS_EXPIRE_TIME, REDIS_EXPIRE_UNIT);
        // 发送消息到Kafka
        ShortUrlMessage message = new ShortUrlMessage(shortUrl.getShortUrl(), originalUrl);
        kafkaProducerService.sendShortUrlMessage(message);
        return shortUrl.getShortUrl();
    }

    @Override
    public Optional<String> getOriginalUrl(String shortCode) {
        // 先从Redis中获取
        String redisKey = REDIS_KEY_PREFIX + shortCode;
        String longUrl = redisTemplate.opsForValue().get(redisKey);

        if (longUrl != null) {
            return Optional.of(longUrl);
        }

        // Redis中没有，从数据库获取
        Optional<ShortUrl> shortUrlOpt = shortUrlRepository.findByShortUrl(shortCode);
        if (shortUrlOpt.isPresent()) {
            ShortUrl shortUrl = shortUrlOpt.get();
            // 更新Redis缓存
            redisTemplate.opsForValue().set(redisKey, shortUrl.getOriginalUrl(), REDIS_EXPIRE_TIME, REDIS_EXPIRE_UNIT);
            return Optional.of(shortUrl.getOriginalUrl());
        }

        return Optional.empty();
    }

    @Override
    public Optional<ShortUrl> getShortUrlInfo(String shortCode) {
        return shortUrlRepository.findByShortUrl(shortCode);
    }

    @Override
    public void addBatch(List<ShortUrl> list) {
        shortUrlRepository.saveAll(list);
    }

    private String generateShortCode() {
        // 生成6位随机字符串
        return java.util.UUID.randomUUID().toString().substring(0, 6);
    }
} 