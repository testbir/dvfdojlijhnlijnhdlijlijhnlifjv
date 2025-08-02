// src/components/skeletons/HomePageSkeleton.tsx

import React from "react";
import "./HomePageSkeleton.scss";

// Отдельный компонент для skeleton баннера
export const BannerSkeleton: React.FC<{ type: "left" | "right" }> = ({ type }) => (
  <div className={`skeleton-banner ${type}`}>
    <div className="skeleton-shimmer"></div>
  </div>
);

// Отдельный компонент для skeleton карточки курса
export const CourseSkeleton: React.FC = () => (
  <div className="skeleton-course-card">
    <div className="skeleton-course-content">
      <div className="skeleton-course-text">
        <div className="skeleton-course-title">
          <div className="skeleton-shimmer"></div>
        </div>
        <div className="skeleton-course-description">
          <div className="skeleton-shimmer"></div>
        </div>
        <div className="skeleton-course-description-line2">
          <div className="skeleton-shimmer"></div>
        </div>
      </div>
      <div className="skeleton-course-avatar">
        <div className="skeleton-shimmer"></div>
      </div>
    </div>
    
    <div className="skeleton-course-footer">
      <div className="skeleton-course-price">
        <div className="skeleton-shimmer"></div>
      </div>
      <div className="skeleton-course-button">
        <div className="skeleton-shimmer"></div>
      </div>
    </div>
  </div>
);

// Основной компонент skeleton для всей HomePage
export const HomePageSkeleton: React.FC = () => {
  return (
    <div className="skeleton-home-homepage">
      {/* Skeleton баннеры */}
      <div className="skeleton-banner-row">
        <BannerSkeleton type="left" />
        <BannerSkeleton type="right" />
      </div>

      {/* Skeleton сетка курсов */}
      <div className="skeleton-course-grid">
        {Array.from({ length: 6 }).map((_, index) => (
          <CourseSkeleton key={index} />
        ))}
      </div>
    </div>
  );
};

export default HomePageSkeleton;