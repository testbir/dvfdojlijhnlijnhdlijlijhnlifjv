// src/pages/HomePage.tsx

import { useEffect, useState, useMemo } from "react";
import { useSearchParams, Link } from "react-router-dom";
import catalogService, { type Course, type Banner } from "../services/catalogService";
import Layout from "../components/Layout";
import HomePageSkeleton from "../components/skeletons/HomePageSkeleton";
import "../styles/HomePage.scss";

export default function HomePage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [banners, setBanners] = useState<Banner[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchParams, setSearchParams] = useSearchParams();
  const [showActivationToast, setShowActivationToast] = useState(false);
  const [loading, setLoading] = useState(true);

  // локальный фильтр
  const filteredCourses = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) return courses;
    return courses.filter(
      c =>
        c.title.toLowerCase().includes(q) ||
        (c.short_description || "").toLowerCase().includes(q)
    );
  }, [courses, searchQuery]);

  // финальная цена
  const getFinalPrice = (c: Course) => {
    if (c.is_free) return 0;
    const percent = c.is_discount_active && c.discount ? c.discount : 0;
    const v = Math.round(c.price * (1 - (percent || 0) / 100));
    return Math.max(0, v);
  };

  const getButtonText = (c: Course) => {
    if (c.is_free) return "ПОЛУЧИТЬ";
    if (c.is_purchased) return "ОТКРЫТЬ";
    return "КУПИТЬ";
  };

  useEffect(() => {
    setLoading(true);
    Promise.all([catalogService.getCourses(), catalogService.getBanners()])
      .then(([coursesResp, bannersResp]) => {
        setCourses((coursesResp.courses || []).sort((a, b) => (a.order ?? 0) - (b.order ?? 0)));
        setBanners(
          (bannersResp || [])
            .sort((a, b) => a.order - b.order)
        );
      })
      .catch(err => console.error("Ошибка загрузки данных:", err))
      .finally(() => {
        setTimeout(() => setLoading(false), 300);
      });
  }, []);

  useEffect(() => {
    if (searchParams.get("message") === "activated") {
      setShowActivationToast(true);
      searchParams.delete("message");
      setSearchParams(searchParams, { replace: true });
      setTimeout(() => setShowActivationToast(false), 8000);
    }
  }, [searchParams, setSearchParams]);

  return (
    <Layout searchQuery={searchQuery} setSearchQuery={setSearchQuery}>
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

      {loading ? (
        <HomePageSkeleton />
      ) : (
        <div className="home-homepage" style={{ animation: "fadeInContent 0.5s ease-out", opacity: 1 }}>
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
            {filteredCourses.map((course) => {
              const finalPrice = getFinalPrice(course);
              const hasDiscount = !course.is_free && course.price > finalPrice;
              return (
                <div key={course.id} className="home-course-card">
                  <div className="home-course-content">
                    <div className="home-course-text">
                      <h3 className="home-course-title">{course.title}</h3>
                      <p className="home-course-description">{course.short_description}</p>
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
                      ) : hasDiscount ? (
                        <div className="home-course-paid">
                          <div className="home-course-original-price">{course.price} ₽</div>
                          <div className="home-course-final-price">{finalPrice} ₽</div>
                        </div>
                      ) : (
                        <span className="home-course-final-price">{finalPrice} ₽</span>
                      )}
                    </div>

                    <Link to={`/course/${course.id}`}>
                      <button className="home-course-button">{getButtonText(course)}</button>
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </Layout>
  );
}
