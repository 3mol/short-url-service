package com.example.shorturl.service;

import com.example.shorturl.entity.ShortUrl;

import java.util.List;
import java.util.Optional;

public interface ShortUrlService {
    
    /**
     * 创建短链接
     * @param originalUrl 原始URL
     * @return 生成的短链接
     */
    String createShortUrl(String originalUrl);
    
    /**
     * 根据短链接获取原始URL
     * @param shortUrl 短链接
     * @return 原始URL
     */
    Optional<String> getOriginalUrl(String shortUrl);
    
    /**
     * 获取短链接信息
     * @param shortUrl 短链接
     * @return 短链接实体
     */
    Optional<ShortUrl> getShortUrlInfo(String shortUrl);

    void addBatch(List<ShortUrl> list);
}