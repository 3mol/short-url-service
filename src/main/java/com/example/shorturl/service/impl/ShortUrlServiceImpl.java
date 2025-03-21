package com.example.shorturl.service.impl;

import com.example.shorturl.entity.ShortUrl;
import com.example.shorturl.message.ShortUrlMessage;
import com.example.shorturl.repository.ShortUrlRepository;
import com.example.shorturl.service.KafkaProducerService;
import com.example.shorturl.service.ShortUrlService;
import jakarta.persistence.EntityManager;
import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;
import java.util.UUID;

@Service
public class ShortUrlServiceImpl implements ShortUrlService {

    private final ShortUrlRepository shortUrlRepository;
    private final KafkaProducerService kafkaProducerService;
    private final EntityManager entityManager;

    @Autowired
    public ShortUrlServiceImpl(ShortUrlRepository shortUrlRepository, KafkaProducerService kafkaProducerService, EntityManager entityManager) {
        this.shortUrlRepository = shortUrlRepository;
        this.kafkaProducerService = kafkaProducerService;
        this.entityManager = entityManager;
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

        // 发送消息到Kafka
        ShortUrlMessage message = new ShortUrlMessage(shortUrl, originalUrl);
        kafkaProducerService.sendShortUrlMessage(message);

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

    @Transactional(rollbackFor = Exception.class)
    public void addBatch(List<ShortUrl> list) {
        shortUrlRepository.saveAllAndFlush(list);
    }

    /**
     * 生成短链接
     *
     * @return 生成的短链接
     */
    private String generateShortUrl() {
        // 使用UUID生成随机字符串并截取前8位
        return UUID.randomUUID().toString().replace("-", "").substring(0, 8);
    }
} 