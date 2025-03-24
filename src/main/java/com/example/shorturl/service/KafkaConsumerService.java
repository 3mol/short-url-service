package com.example.shorturl.service;

import com.example.shorturl.entity.ShortUrl;
import com.example.shorturl.message.ShortUrlMessage;
import com.example.shorturl.repository.ShortUrlRepository;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.annotation.Resource;
import jakarta.persistence.EntityManager;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class KafkaConsumerService {
    private static final Logger log = LoggerFactory.getLogger(KafkaConsumerService.class);
    private final ShortUrlService shortUrlService;
    private final ObjectMapper objectMapper;
    @Resource
    EntityManager entityManager;

    @Autowired
    public KafkaConsumerService(ShortUrlService shortUrlService, ObjectMapper objectMapper) {
        this.shortUrlService = shortUrlService;
        this.objectMapper = objectMapper;
    }

    @KafkaListener(
       topicPattern = KafkaProducerService.TOPIC,
       groupId = "short-url-group",
       containerFactory = "batchFactory",
       properties = {"max.poll.records=200",
          "fetch.min.bytes=1",
          "fetch.max.wait.ms=500"})
    public void listen(List<String> messages) {
        final var list = messages.stream().map(msg -> {
            ShortUrlMessage shortUrlMessage = null;
            try {
                shortUrlMessage = objectMapper.readValue(msg, ShortUrlMessage.class);
            } catch (JsonProcessingException e) {
                throw new RuntimeException(e);
            }
            return new ShortUrl(shortUrlMessage.getShortUrl(), shortUrlMessage.getOriginalUrl());
        }).toList();
        log.info("save size:{}", list.size());
        shortUrlService.addBatch(list);
    }
}