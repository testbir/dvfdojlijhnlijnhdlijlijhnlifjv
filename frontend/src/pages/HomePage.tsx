// frontend/src/pages/HomePage.tsx

import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import courseService from "../services/courseService";
import catalogService from "../services/catalogService"; // для баннеров и CDN
import { Link } from "react-router-dom";
import Layout from "../components/Layout";
import HomePageSkeleton from "../components/skeletons/HomePageSkeleton";
import "../styles/HomePage.scss";

export default function HomePage() {
  const [courses, setCourses] = useState<any[]>([]);
  const [banners, setBanners] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchParams, setSearchParams] = useSearchParams();
  const [showActivationToast, setShowActivationToast] = useState(false);
  const [loading, setLoading] = useState(true);

  // Фильтрация курсов
  const filteredCourses = courses.filter(course => 
    searchQuery.trim() === "" ||
    course.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    course.short_description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        // Загружаем курсы через новый API
        const coursesResponse = await courseService.getCourses();
        setCourses(coursesResponse.courses || []);
        
        // Загружаем баннеры через старый catalogService
        const bannersData = await catalogService.getBanners(2);
        setBanners(bannersData);
      } catch (error) {
        console.error("Ошибка загрузки данных:", error);
      } finally {
        setTimeout(() => setLoading(false), 300);
      }
    };

    loadData();
  }, []);

  // Обработка уведомления об активации
  useEffect(() => {
    if (searchParams.get('message') === 'activated') {
      setShowActivationToast(true);
      searchParams.delete('message');
      setSearchParams(searchParams, { replace: true });
      setTimeout(() => setShowActivationToast(false), 8000);
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
              <div className="toast-subtitle">Теперь вы можете использовать все возможности</div>
            </div>
            <button className="toast-close" onClick={() => setShowActivationToast(false)}>×</button>
          </div>
        </div>
      )}

      {loading ? (
        <HomePageSkeleton />
      ) : (
        <div className="home-page">
          {/* Баннеры */}
          {banners.length > 0 && (
            <div className="banners-section">
              {banners.map((banner) => (
                <div key={banner.id} className="banner">
                  {banner.link ? (
                    <a href={banner.link} target="_blank" rel="noopener noreferrer">
                      <img 
                        src={catalogService.formatImageUrl(banner.image)} 
                        alt="Баннер" 
                      />
                    </a>
                  ) : (
                    <img 
                      src={catalogService.formatImageUrl(banner.image)} 
                      alt="Баннер" 
                    />
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Курсы */}
          <div className="courses-grid">
            {filteredCourses.map((course) => (
              <Link
                key={course.id}
                to={`/course/${course.id}`}
                className="course-card"
              >
                <div className="course-image">
                  <img 
                    src={catalogService.formatImageUrl(course.image)} 
                    alt={course.title} 
                  />
                  {course.is_free && (
                    <span className="free-badge">Бесплатно</span>
                  )}
                </div>
                <div className="course-content">
                  <h3 className="course-title">{course.title}</h3>
                  <p className="course-description">{course.short_description}</p>
                  {!course.is_free && (
                    <div className="course-price">
                      {course.discount ? (
                        <>
                          <span className="price-old">{course.price} ₽</span>
                          <span className="price-current">
                            {Math.round(course.price * (1 - course.discount / 100))} ₽
                          </span>
                        </>
                      ) : (
                        <span className="price-current">{course.price} ₽</span>
                      )}
                    </div>
                  )}
                </div>
              </Link>
            ))}
          </div>

          {filteredCourses.length === 0 && (
            <div className="no-courses">
              <p>Курсы не найдены</p>
            </div>
          )}
        </div>
      )}
    </Layout>
  );
}