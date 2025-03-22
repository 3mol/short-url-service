package com.example.shorturl.repository;

import com.example.shorturl.entity.ShortUrl;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface ShortUrlRepository extends JpaRepository<ShortUrl, Long> {
    /**
     * 根据短链接查询记录
     * @param shortUrl 短链接
     * @return 短链接对象
     */
    Optional<ShortUrl> findByShortUrl(String shortUrl);
    
    /**
     * 根据原始URL查询记录
     * @param originalUrl 原始URL
     * @return 短链接对象
     */
    Optional<ShortUrl> findByOriginalUrl(String originalUrl);
} 