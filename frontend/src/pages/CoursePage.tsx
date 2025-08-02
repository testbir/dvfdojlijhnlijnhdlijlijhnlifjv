// frontend/src/pages/CoursePage.tsx

import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import catalogService, { type CourseDetail } from "../services/catalogService";
import { useAuth } from "../hooks/useAuth";
import Layout from "../components/Layout";
import VideoPlayer from "../components/VideoPlayer";
import AuthModal from "../components/AuthModal";
import CourseModal from "../components/CourseModal";
import "../styles/CoursePage.scss";

interface CourseModalData {
  title: string;
  blocks: Array<{
    type: 'text' | 'image';
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

  const parts = [];
  if (hours) parts.push(`${hours}ч`);
  if (minutes || hours) parts.push(`${minutes}м`);
  parts.push(`${secs}с`);
  return parts.join(" ");
}

export default function CoursePage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  
  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [courseModal, setCourseModal] = useState<CourseModalData | null>(null);
  const [studentWorks, setStudentWorks] = useState<StudentWorksData | null>(null);
  const [videoError, setVideoError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [showVideo, setShowVideo] = useState(false);
  const [showCourseModal, setShowCourseModal] = useState(false);
  const [discountSecondsLeft, setDiscountSecondsLeft] = useState<number | null>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  // Определяем, мобильное ли устройство
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 950);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  useEffect(() => {
    if (!id) return;

    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Загружаем основные данные курса
        const data = await catalogService.getFullCourseData(Number(id));
        setCourse(data.course);
        
        // Загружаем модальное окно курса
        try {
          const modalResponse = await fetch(`http://localhost:8001/courses/${id}/modal`);
          if (modalResponse.ok) {
            const modalData = await modalResponse.json();
            if (modalData) {
              setCourseModal(modalData);
            }
          }
        } catch (error) {
          console.log("Модальное окно не настроено для этого курса");
        }
        
        // Загружаем работы учеников
        try {
          const worksResponse = await fetch(`http://localhost:8001/courses/${id}/student-works`);
          if (worksResponse.ok) {
            const worksData = await worksResponse.json();
            if (worksData) {
              setStudentWorks(worksData);
            }
          }
        } catch (error) {
          console.log("Работы учеников не настроены для этого курса");
        }
        
      } catch (error) {
        console.error("Ошибка загрузки данных курса:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  useEffect(() => {
    if (
      course?.is_discount_active &&
      course.discount_ends_in &&
      course.discount_ends_in > 0
    ) {
      setDiscountSecondsLeft(Math.floor(course.discount_ends_in));
    }
  }, [course]);

  useEffect(() => {
    if (!discountSecondsLeft || discountSecondsLeft <= 0) return;

    const interval = setInterval(() => {
      setDiscountSecondsLeft(prev =>
        prev !== null && prev > 0 ? prev - 1 : 0
      );
    }, 1000);

    return () => clearInterval(interval);
  }, [discountSecondsLeft]);

  const handleVideoError = (error: string) => {
    setVideoError(error);
    console.error("Ошибка видеоплеера:", error);
  };

  const handlePurchase = async () => {
    if (!course || course.is_free) return;

    if (!isAuthenticated) {
      setShowAuthModal(true);
      return;
    }

    try {
      const response = await catalogService.buyCourse(course.id, {
        payment_id: "dummy_payment_id"
      });

      if (response.success) {
        setCourse({ ...course, has_access: true, button_text: "ОТКРЫТЬ" });
        alert("Курс успешно приобретен!");
      }
    } catch (error) {
      console.error("Ошибка при покупке курса:", error);
      alert("Ошибка при покупке курса. Попробуйте снова.");
    }
  };

  const handleRegister = () => {
    setShowAuthModal(false);
    navigate('/register');
  };

  const handleLogin = () => {
    setShowAuthModal(false);
    navigate('/login');
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
              {/* Левая колонка: видео и описание */}
              <div className="course-content">
                <div className="course-buttons-group">
                  <button 
                    className="video-toggle-button"
                    onClick={() => setShowVideo(prev => !prev)}
                  >
                    {showVideo ? "Скрыть видео" : "Смотреть о курсе"}
                    <span
                      className="material-symbols-outlined"
                      style={{
                        transform: `rotate(${showVideo ? 90 : 0}deg)`,
                      }}
                    >
                      arrow_forward_ios
                    </span>
                  </button>

                  {courseModal && (
                    <button 
                      className="program-button"
                      onClick={() => setShowCourseModal(true)}
                    >
                      💡 Программа курса
                    </button>
                  )}
                </div>

                <div className={`video-section-wrapper ${showVideo ? "open" : ""}`}>
                  {course.video && (
                    <div className="video-container">
                        <VideoPlayer
                          masterPlaylistUrl={course.video}
                          poster={course.video_preview ? catalogService.formatImageUrl(course.video_preview) : undefined}
                          onError={handleVideoError}
                          className="course-video-player"
                        />
                      {videoError && (
                        <div className="video-error">
                          <p>⚠️ {videoError}</p>
                          <button onClick={() => window.location.reload()}>
                            Перезагрузить страницу
                          </button>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                <div
                  className="course-description"
                  dangerouslySetInnerHTML={{ __html: course.full_description }}
                />
              </div>

              {/* Правая колонка: цена и кнопка - только для десктопа */}
              {!isMobile && (
                <div className="course-purchase-sidebar">
                  <div className="price-section">
                    {discountSecondsLeft !== null && discountSecondsLeft > 0 && (
                      <p className="discount-timer">
                        Осталось {formatCountdown(discountSecondsLeft)}
                      </p>
                    )}

                    {course.is_free ? (
                      <span className="course-free">Бесплатно</span>
                    ) : course.price > course.final_price ? (
                      <div className="course-paid">
                        <div className="course-final-price-wrapper">
                          <span className="course-original-price">{course.price} ₽</span>
                          <span className="course-final-price">{course.final_price} ₽</span>
                          <span className="discount-percent">
                            &minus;{Math.round(((course.price - course.final_price) / course.price) * 100)}%
                          </span>
                        </div>
                      </div>
                    ) : (
                      <span className="course-final-price">{course.final_price} ₽</span>
                    )}
                  </div>

                  <button 
                    className={`course-button ${course.has_access ? 'accessed' : ''}`}
                    onClick={course.has_access ? undefined : handlePurchase}
                    disabled={course.has_access}
                  >
                    {course.button_text}
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Блок работ учеников */}
          {studentWorks && (
            <div className="student-works-section">
              <h2 className="section-title">{studentWorks.title}</h2>
              <p className="section-description">{studentWorks.description}</p>
              
              <div className="works-grid">
                {studentWorks.works.sort((a, b) => a.order - b.order).map((work, index) => (
                  <div key={index} className="work-item">
                    <div className="work-image">
                      <img 
                        src={catalogService.formatImageUrl(work.image)} 
                        alt={work.description}
                      />
                    </div>
                    <div className="work-info">
                      {work.description && (
                        <p className="work-description">{work.description}</p>
                      )}
                      {work.bot_tag && (
                        <a 
                          href={`https://t.me/${work.bot_tag.replace('@', '')}`}
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

          {/* Модальное окно программы курса */}
          {courseModal && (
            <CourseModal
              isOpen={showCourseModal}
              onClose={() => setShowCourseModal(false)}
              title={courseModal.title}
              blocks={courseModal.blocks}
              imageFormatter={(url) => catalogService.formatImageUrl(url)}
            />
          )}

          {/* Модальное окно авторизации */}
          <AuthModal
            isOpen={showAuthModal}
            onClose={() => setShowAuthModal(false)}
            onRegister={handleRegister}
            onLogin={handleLogin}
            courseTitle={course?.title}
            coursePrice={course?.final_price}
          />
        </div>
      </Layout>

      {/* Фиксированный блок оплаты для мобильных устройств - вне Layout */}
      {isMobile && (
        <div className="course-purchase-sidebar mobile-fixed">
          <div className="price-section">
            {discountSecondsLeft !== null && discountSecondsLeft > 0 && (
              <p className="discount-timer">
                Осталось {formatCountdown(discountSecondsLeft)}
              </p>
            )}

            {course.is_free ? (
              <span className="course-free">Бесплатно</span>
            ) : course.price > course.final_price ? (
              <div className="course-paid">
                <div className="course-final-price-wrapper">
                  <span className="course-original-price">{course.price} ₽</span>
                  <span className="course-final-price">{course.final_price} ₽</span>
                  <span className="discount-percent">
                    &minus;{Math.round(((course.price - course.final_price) / course.price) * 100)}%
                  </span>
                </div>
              </div>
            ) : (
              <span className="course-final-price">{course.final_price} ₽</span>
            )}
          </div>

          <button 
            className={`course-button ${course.has_access ? 'accessed' : ''}`}
            onClick={course.has_access ? undefined : handlePurchase}
            disabled={course.has_access}
          >
            {course.button_text}
          </button>
        </div>
      )}
    </>
  );
}