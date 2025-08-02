// src/pages/HomePage.tsx

import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import catalogService, { type Course, type Banner } from "../services/catalogService";
import { Link } from "react-router-dom";
import Layout from "../components/Layout";
import HomePageSkeleton from "../components/skeletons/HomePageSkeleton";
import "../styles/HomePage.scss";

export default function HomePage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [banners, setBanners] = useState<Banner[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchParams, setSearchParams] = useSearchParams();
  const [showActivationToast, setShowActivationToast] = useState(false);
  const [loading, setLoading] = useState(true); // ✅ Добавил состояние загрузки
  
  const filteredCourses = catalogService.filterCourses(courses, searchQuery);

  useEffect(() => {
    setLoading(true); // ✅ Начинаем загрузку
    
    catalogService.getHomePageData()
      .then((data) => {
        setCourses(data.courses);
        setBanners(data.banners);
      })
      .catch((err) => console.error("Ошибка загрузки данных:", err))
      .finally(() => {
        // ✅ Минимальная задержка для плавного перехода от skeleton
        setTimeout(() => {
          setLoading(false);
        }, 300);
      });
  }, []);

  useEffect(() => {
    // Проверяем параметр активации
    if (searchParams.get('message') === 'activated') {
      setShowActivationToast(true);
      
      // Убираем параметр из URL
      searchParams.delete('message');
      setSearchParams(searchParams, { replace: true });
      
      // Автоматически скрываем через 5 секунд
      setTimeout(() => {
        setShowActivationToast(false);
      }, 8000);
    }
  }, [searchParams, setSearchParams]);

  return (
    <Layout searchQuery={searchQuery} setSearchQuery={setSearchQuery}>
      {/* Тост-уведомление об активации */}
      {showActivationToast && (
        <div className="activation-toast">
          <div className="toast-content">
            <span className="toast-icon">✅</span>
            <div className="toast-text">
              <div className="toast-title">Аккаунт активирован!</div>
              <div className="toast-subtitle">Войдите для продолжения</div>
            </div>
            <button className="toast-close" onClick={() => setShowActivationToast(false)}>×</button>
          </div>
        </div>
      )}

      {/* ✅ Показываем skeleton пока идет загрузка */}
      {loading ? (
        <HomePageSkeleton />
      ) : (
        <div className="home-homepage" style={{ 
          animation: 'fadeInContent 0.5s ease-out',
          opacity: 1 
        }}>
          <div className="home-banner-row">
            {banners.map((banner, index) => {
              const image = (
                <img
                  key={`banner-${banner.id}`}
                  src={catalogService.formatImageUrl(banner.image)}
                  alt={`Баннер ${index + 1}`}
                  className={`home-homepage-banner ${index === 0 ? "left" : "right"}`}
                  onError={(e) => (e.currentTarget.src = "/fallback.png")}
                />
              );

              return banner.link ? (
                <a
                  key={banner.id}
                  href={banner.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ display: "block", position: "relative", zIndex: 2 }}
                >
                  {image}
                </a>
              ) : (
                image
              );
            })}
          </div>

          <div className="home-course-grid">
            {filteredCourses.map((course) => (
              <div key={course.id} className="home-course-card">
                <div className="home-course-content">
                  <div className="home-course-text">
                    <h3 className="home-course-title">{course.title}</h3>
                    <p className="home-course-description">
                      {course.short_description}
                    </p>
                  </div>
                  <img
                    src={catalogService.formatImageUrl(course.image)}
                    alt={course.title}
                    onError={(e) => (e.currentTarget.src = "/fallback.png")}
                    className="home-course-avatar"
                  />
                </div>

                <div className="home-course-footer">
                  <div className="home-course-price">
                    {course.is_free ? (
                      <span className="home-course-free">Бесплатно</span>
                    ) : course.price > course.final_price ? (
                      <div className="home-course-paid">
                        <div className="home-course-original-price">
                          {course.price} ₽
                        </div>
                        <div className="home-course-final-price">
                          {course.final_price} ₽
                        </div>
                      </div>
                    ) : (
                      <span className="home-course-final-price">
                        {course.final_price} ₽
                      </span>
                    )}
                  </div>

                  <Link to={`/course/${course.id}`}>
                    <button className="home-course-button">{course.button_text}</button>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </Layout>
  );
}