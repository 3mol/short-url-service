package com.example.shorturl.service;

import com.example.shorturl.message.ShortUrlMessage;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.annotation.Resource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

@Service
public class KafkaProducerService {
    public static final String TOPIC = "short-url-topic";
    @Resource
    private KafkaTemplate<String, String> kafkaTemplate;
    private final ObjectMapper objectMapper;

    @Autowired
    public KafkaProducerService(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    public void sendShortUrlMessage(ShortUrlMessage message) {
        try {
            String messageJson = objectMapper.writeValueAsString(message);
            kafkaTemplate.send(TOPIC, message.getShortUrl(), messageJson);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Error converting message to JSON", e);
        }
    }
} 