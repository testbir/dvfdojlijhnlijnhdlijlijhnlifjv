// frontend/src/pages/CoursePage.tsx

import { useEffect, useState, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import catalogService, { type Course as CatalogCourse } from "../services/catalogService";
import { catalogApi } from "../api/axiosInstance";
import { useAuth } from "../hooks/useAuth";
import Layout from "../components/Layout";
import VideoPlayer from "../components/VideoPlayer";
import AuthModal from "../components/AuthModal";
import CourseModal from "../components/CourseModal";
import "../styles/CoursePage.scss";

interface CourseModalData {
  title: string;
  blocks: Array<{
    type: "text" | "image";
    content: string;
    order: number;
  }>;
}

interface StudentWorksData {
  title: string;
  description: string;
  works: Array<{
    image: string;
    description: string;
    bot_tag: string;
    order: number;
  }>;
}

function formatCountdown(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  const parts: string[] = [];
  if (hours) parts.push(`${hours}ч`);
  if (minutes || hours) parts.push(`${minutes}м`);
  parts.push(`${secs}с`);
  return parts.join(" ");
}

export default function CoursePage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [course, setCourse] = useState<CatalogCourse | null>(null);
  const [courseModal, setCourseModal] = useState<CourseModalData | null>(null);
  const [studentWorks, setStudentWorks] = useState<StudentWorksData | null>(null);
  const [videoError, setVideoError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [showVideo, setShowVideo] = useState(false);
  const [showCourseModal, setShowCourseModal] = useState(false);
  const [discountSecondsLeft, setDiscountSecondsLeft] = useState<number | null>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  // мобильность
  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth <= 950);
    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  // загрузка данных
  useEffect(() => {
    if (!id) return;

    const fetchData = async () => {
      try {
        setLoading(true);

        // основной курс
        const data = await catalogService.getCourseDetail(Number(id));
        setCourse(data);

        // модалка с программой
        try {
          const modalResp = await catalogApi.get(`/v1/public/courses/${id}/modal/`);
          if (modalResp?.data) setCourseModal(modalResp.data);
        } catch {
          // нет модалки
        }

        // работы учеников
        try {
          const worksResp = await catalogApi.get(`/v1/public/courses/${id}/student-works/`);
          if (worksResp?.data) setStudentWorks(worksResp.data);
        } catch {
          // нет работ
        }
      } catch (error) {
        console.error("Ошибка загрузки данных курса:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  // таймер скидки
  useEffect(() => {
    if (!course?.is_discount_active || !course.discount_until) {
      setDiscountSecondsLeft(null);
      return;
    }
    const end = new Date(course.discount_until).getTime();
    const now = Date.now();
    const left = Math.max(0, Math.floor((end - now) / 1000));
    setDiscountSecondsLeft(left);
  }, [course?.is_discount_active, course?.discount_until]);

  useEffect(() => {
    if (!discountSecondsLeft || discountSecondsLeft <= 0) return;
    const interval = setInterval(() => {
      setDiscountSecondsLeft((prev) => (prev !== null && prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(interval);
  }, [discountSecondsLeft]);

  const handleVideoError = (error: string) => {
    setVideoError(error);
    console.error("Ошибка видеоплеера:", error);
  };

  // производные
  const hasAccess = useMemo(() => {
    if (!course) return false;
    return course.is_free || !!course.is_purchased;
  }, [course]);

  const finalPrice = useMemo(() => {
    if (!course) return 0;
    if (course.is_free) return 0;
    const percent = course.is_discount_active && course.discount ? course.discount : 0;
    const raw = Math.round(course.price * (1 - (percent || 0) / 100));
    return Math.max(0, raw);
  }, [course]);

  const buttonText = useMemo(() => {
    if (!course) return "ЗАГРУЗКА";
    if (hasAccess) return "ОТКРЫТЬ";
    return course.is_free ? "ПОЛУЧИТЬ" : "КУПИТЬ";
  }, [course, hasAccess]);

  const videoUrl = useMemo(() => {
    if (!course?.video) return "";
    const base = catalogService.formatVideoUrl(course.video);
    if (base.includes(".m3u8")) {
      const sep = base.includes("?") ? "&" : "?";
      const version = course.is_discount_active ? `${course.id}_discount` : `${course.id}_regular`;
      return `${base}${sep}v=${version}`;
    }
    return base;
  }, [course?.video, course?.is_discount_active, course?.id]);

  const handleOpenCourse = () => {
    if (!course) return;
    navigate(`/course/${course.id}/learn`);
  };

  const handlePurchase = async () => {
    if (!course || course.is_free) return;

    if (!isAuthenticated) {
      setShowAuthModal(true);
      return;
    }

    try {
      const response = await catalogService.buyCourse(course.id);
      if (response.success) {
        setCourse({ ...course, is_purchased: true });
        alert("Курс успешно приобретен");
      } else {
        alert(response.message || "Не удалось купить курс");
      }
    } catch (error) {
      console.error("Ошибка при покупке курса:", error);
      alert("Ошибка при покупке курса. Попробуйте снова.");
    }
  };

  const handleRegister = () => {
    setShowAuthModal(false);
    navigate("/register");
  };

  const handleLogin = () => {
    setShowAuthModal(false);
    navigate("/login");
  };

  if (loading) {
    return (
      <Layout>
        <div className="course-page">
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>Загрузка курса...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (!course) {
    return (
      <Layout>
        <div className="course-page">
          <div className="error-message">
            <h2>Курс не найден</h2>
            <p>Запрашиваемый курс не существует или был удален.</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <>
      <Layout>
        <div className="course-page">
          <div className="course-main">
            <h1>{course.title}</h1>

            {course.banner_text && (
              <div
                className="course-banner"
                style={{
                  background: `linear-gradient(35deg, ${course.banner_color_left} 30%, ${course.banner_color_right} 60%)`,
                }}
              >
                <div className="banner-content">
                  <img
                    src={catalogService.formatImageUrl(course.image)}
                    alt={course.title}
                    className="banner-image"
                  />
                  <p className="banner-text">{course.banner_text}</p>
                </div>
              </div>
            )}

            <div className="course-content-layout">
              {/* Левая колонка */}
              <div className="course-content">
                <div className="course-buttons-group">
                  <button className="video-toggle-button" onClick={() => setShowVideo((p) => !p)}>
                    {showVideo ? "Скрыть видео" : "Смотреть о курсе"}
                    <span
                      className="material-symbols-outlined"
                      style={{ transform: `rotate(${showVideo ? 90 : 0}deg)` }}
                    >
                      arrow_forward_ios
                    </span>
                  </button>

                  {courseModal && (
                    <button className="program-button" onClick={() => setShowCourseModal(true)}>
                      💡 Программа курса
                    </button>
                  )}
                </div>

                <div className={`video-section-wrapper ${showVideo ? "open" : ""}`}>
                  {course.video && showVideo && (
                    <div className="video-container">
                      <VideoPlayer
                        key={`video-${course.id}-${course.is_discount_active ? "dis" : "reg"}`}
                        videoUrl={videoUrl}
                        onError={handleVideoError}
                        className="course-video-player"
                      />
                      {videoError && (
                        <div className="video-error">
                          <p>⚠️ {videoError}</p>
                          <button onClick={() => window.location.reload()}>Перезагрузить страницу</button>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                <div
                  className="course-description"
                  dangerouslySetInnerHTML={{ __html: course.full_description || "" }}
                />
              </div>

              {/* Правая колонка: цена и кнопка (десктоп) */}
              {!isMobile && (
                <div className="course-purchase-sidebar">
                  <div className="price-section">
                    {discountSecondsLeft !== null && discountSecondsLeft > 0 && (
                      <p className="discount-timer">Осталось {formatCountdown(discountSecondsLeft)}</p>
                    )}

                    {course.is_free ? (
                      <span className="course-free">Бесплатно</span>
                    ) : course.price > finalPrice ? (
                      <div className="course-paid">
                        <div className="course-final-price-wrapper">
                          <span className="course-original-price">{course.price} ₽</span>
                          <span className="course-final-price">{finalPrice} ₽</span>
                          <span className="discount-percent">
                            &minus;{Math.round(((course.price - finalPrice) / course.price) * 100)}%
                          </span>
                        </div>
                      </div>
                    ) : (
                      <span className="course-final-price">{finalPrice} ₽</span>
                    )}
                  </div>

                  <button
                    className={`course-button ${hasAccess ? "accessed" : ""}`}
                    onClick={hasAccess ? handleOpenCourse : handlePurchase}
                  >
                    {buttonText}
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Работы учеников */}
          {studentWorks && (
            <div className="student-works-section">
              <h2 className="section-title">{studentWorks.title}</h2>
              <p className="section-description">{studentWorks.description}</p>

              <div className="works-grid">
                {studentWorks.works
                  .sort((a, b) => a.order - b.order)
                  .map((work, index) => (
                    <div key={index} className="work-item">
                      <div className="work-image">
                        <img src={catalogService.formatImageUrl(work.image)} alt={work.description} />
                      </div>
                      <div className="work-info">
                        {work.description && <p className="work-description">{work.description}</p>}
                        {work.bot_tag && (
                          <a
                            href={`https://t.me/${work.bot_tag.replace("@", "")}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="work-link"
                          >
                            {work.bot_tag}
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {/* Модалка программы */}
          {courseModal && (
            <CourseModal
              isOpen={showCourseModal}
              onClose={() => setShowCourseModal(false)}
              title={courseModal.title}
              blocks={courseModal.blocks}
              imageFormatter={(url) => catalogService.formatImageUrl(url)}
            />
          )}

          {/* Модалка авторизации */}
          <AuthModal
            isOpen={showAuthModal}
            onClose={() => setShowAuthModal(false)}
            onRegister={handleRegister}
            onLogin={handleLogin}
            courseTitle={course?.title}
            coursePrice={finalPrice}
          />
        </div>
      </Layout>

      {/* Фиксированный блок оплаты для мобильных устройств */}
      {isMobile && (
        <div className="course-purchase-sidebar mobile-fixed">
          <div className="price-section">
            {discountSecondsLeft !== null && discountSecondsLeft > 0 && (
              <p className="discount-timer">Осталось {formatCountdown(discountSecondsLeft)}</p>
            )}

            {course.is_free ? (
              <span className="course-free">Бесплатно</span>
            ) : course.price > finalPrice ? (
              <div className="course-paid">
                <div className="course-final-price-wrapper">
                  <span className="course-original-price">{course.price} ₽</span>
                  <span className="course-final-price">{finalPrice} ₽</span>
                  <span className="discount-percent">
                    &minus;{Math.round(((course.price - finalPrice) / course.price) * 100)}%
                  </span>
                </div>
              </div>
            ) : (
              <span className="course-final-price">{finalPrice} ₽</span>
            )}
          </div>
          <button
            className={`course-button ${hasAccess ? "accessed" : ""}`}
            onClick={hasAccess ? handleOpenCourse : handlePurchase}
          >
            {buttonText}
          </button>
        </div>
      )}
    </>
  );
}
