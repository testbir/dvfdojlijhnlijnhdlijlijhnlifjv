import React, { useRef, useEffect, useState, useCallback } from 'react';
import { 
  Play, 
  Pause, 
  Volume2, 
  VolumeX,
  Maximize,
  Minimize,
  PlayCircle,
  Loader
} from 'lucide-react';
import Hls from 'hls.js';

const isMobile = () =>
  /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

interface VideoPlayerProps {
  videoUrl: string;
  poster?: string;
  className?: string;
  onError?: (_error: string) => void;
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({
  videoUrl,
  poster,
  className = '',
  onError = () => {} // Значение по умолчанию
}) => {

  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);
  const hlsRef = useRef<Hls | null>(null);
  
  // States
  
  const [isLoading, setIsLoading] = useState(true);
  const [isBuffering, setIsBuffering] = useState(false);
  const [isControlsVisible, setIsControlsVisible] = useState(true);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [buffered, setBuffered] = useState(0);
  const [volume, setVolume] = useState(1);
  const [previousVolume, setPreviousVolume] = useState(1);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [isRateMenuOpen, setIsRateMenuOpen] = useState(false);
  const [showVolumeSlider, setShowVolumeSlider] = useState(false);
  const [, setIsSeeking] = useState(false);
  const [seekTime, setSeekTime] = useState<number | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState(0);
  const [showCenterPlay, setShowCenterPlay] = useState(true);
  const [hasInteracted, setHasInteracted] = useState(false);
  
  const controlsTimeoutRef = useRef<number | null>(null);
  const volumeHideTimeoutRef = useRef<number | null>(null);

  // Inject CSS styles
  useEffect(() => {
    const styleSheet = document.createElement('style');
    styleSheet.textContent = `
      @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
      }
      
      .video-player-container input[type="range"]::-webkit-slider-thumb {
        appearance: none;
        width: 12px;
        height: 12px;
        background: #ff0000;
        border-radius: 50%;
        cursor: pointer;
      }
      
      .video-player-container input[type="range"]::-moz-range-thumb {
        width: 12px;
        height: 12px;
        background: #ff0000;
        border-radius: 50%;
        cursor: pointer;
        border: none;
      }
      
      .video-player-container button:hover {
        background-color: rgba(255,255,255,0.1) !important;
      }
      
      .video-player-container .menu-item:hover {
        background-color: rgba(255,255,255,0.2) !important;
      }
      
      .video-player-container *:focus {
        outline: none;
      }
      
      .video-player-container .center-play-container:hover svg {
        transform: scale(1.1);
      }
      
      /* Custom scrollbar for menus */
      .video-player-container ::-webkit-scrollbar {
        width: 4px;
      }
      
      .video-player-container ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.1);
        border-radius: 2px;
      }
      
      .video-player-container ::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,0.3);
        border-radius: 2px;
      }
      
      /* Progress bar hover effect */
      @media (hover: hover) {
        .video-player-container .progress-container:hover {
          height: 7px !important;
        }
        
        .video-player-container .progress-container:hover .progress-scrubber {
          width: 16px !important;
          height: 16px !important;
        }
      }
    `;

    if (!document.getElementById('video-player-styles')) {
      styleSheet.id = 'video-player-styles';
      document.head.appendChild(styleSheet);
    }

    return () => {
      const existingStyles = document.getElementById('video-player-styles');
      if (existingStyles && existingStyles.parentNode) {
        existingStyles.parentNode.removeChild(existingStyles);
      }
    };
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (!videoRef.current || !hasInteracted || isMobile()) return;
      
      const video = videoRef.current;
      
      switch(e.key.toLowerCase()) {
        case ' ':
        case 'k':
          e.preventDefault();
          togglePlay();
          break;
        case 'f':
          e.preventDefault();
          toggleFullscreen();
          break;
        case 'm':
          e.preventDefault();
          toggleMute();
          break;
        case 'arrowleft':
          e.preventDefault();
          video.currentTime = Math.max(0, video.currentTime - 5);
          break;
        case 'arrowright':
          e.preventDefault();
          video.currentTime = Math.min(video.duration, video.currentTime + 5);
          break;
        case 'j':
          e.preventDefault();
          video.currentTime = Math.max(0, video.currentTime - 10);
          break;
        case 'l':
          e.preventDefault();
          video.currentTime = Math.min(video.duration, video.currentTime + 10);
          break;
        case 'arrowup':
          e.preventDefault();
          handleVolumeChange(Math.min(1, volume + 0.05));
          break;
        case 'arrowdown':
          e.preventDefault();
          handleVolumeChange(Math.max(0, volume - 0.05));
          break;
        case ',':
          if (video.paused) {
            e.preventDefault();
            video.currentTime = Math.max(0, video.currentTime - 1/30);
          }
          break;
        case '.':
          if (video.paused) {
            e.preventDefault();
            video.currentTime = Math.min(video.duration, video.currentTime + 1/30);
          }
          break;
        case '<':
          e.preventDefault();
          changePlaybackRate(Math.max(0.25, playbackRate - 0.25));
          break;
        case '>':
          e.preventDefault();
          changePlaybackRate(Math.min(2, playbackRate + 0.25));
          break;
        case '0':
        case '1':
        case '2':
        case '3':
        case '4':
        case '5':
        case '6':
        case '7':
        case '8':
        case '9':
          e.preventDefault();
          const percent = parseInt(e.key) * 10;
          video.currentTime = (video.duration * percent) / 100;
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [hasInteracted, volume, playbackRate]);


useEffect(() => {
  const video = videoRef.current;
  if (!video || !videoUrl) return;

  const setupVideo = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Проверяем, является ли URL HLS плейлистом
      const isHLS = videoUrl.includes('.m3u8');

      if (isHLS) {
        // Используем HLS.js для m3u8 файлов
        if (Hls.isSupported()) {
          // Уничтожаем предыдущий экземпляр
          if (hlsRef.current) {
            hlsRef.current.destroy();
          }

          const hls = new Hls({
            enableWorker: true,
            lowLatencyMode: false,
            backBufferLength: 90,
          });

          hlsRef.current = hls;

          hls.on(Hls.Events.ERROR, (_event, data) => {
            console.error('HLS Error:', data);
            if (data.fatal) {
              const errorMsg = 'Ошибка загрузки видео. Проверьте подключение к интернету.';
              setError(errorMsg);
              if (onError) onError(errorMsg);
            }
          });

          hls.on(Hls.Events.MANIFEST_PARSED, () => {
            setIsLoading(false);
            video.play().catch(e => console.log('Autoplay prevented:', e));
          });

          hls.loadSource(videoUrl);
          hls.attachMedia(video);
        } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
          // Для Safari, который поддерживает HLS нативно
          video.src = videoUrl;
          video.addEventListener('loadedmetadata', () => setIsLoading(false));
        } else {
          const errorMsg = 'Ваш браузер не поддерживает воспроизведение HLS видео';
          setError(errorMsg);
          if (onError) onError(errorMsg);
        }
      } else {
        // Для обычных видео файлов (mp4, webm)
        video.src = videoUrl;
        video.addEventListener('loadedmetadata', () => setIsLoading(false));
      }
    } catch (err) {
      const errorMsg = 'Ошибка инициализации видео плеера';
      setError(errorMsg);
      if (onError) onError(errorMsg);
      console.error('Video setup error:', err);
    }
  };

  setupVideo();

  // Cleanup
  return () => {
    if (hlsRef.current) {
      hlsRef.current.destroy();
      hlsRef.current = null;
    }
  };
}, [videoUrl, onError]);

  // Video event handlers
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleTimeUpdate = () => {
      setCurrentTime(video.currentTime);
      updateBuffered();
    };
    
    const handleDurationChange = () => setDuration(video.duration);
    const handlePlay = () => {
      setIsPlaying(true);
      setShowCenterPlay(false);
    };
    const handlePause = () => setIsPlaying(false);
    const handleLoadStart = () => setIsLoading(true);
    const handleCanPlay = () => {
      setIsLoading(false);
      setIsBuffering(false);
    };
    const handleWaiting = () => setIsBuffering(true);
    const handlePlaying = () => setIsBuffering(false);
    const handleVolumeChange = () => setVolume(video.volume);
    const handleRateChange = () => setPlaybackRate(video.playbackRate);
    const handleEnded = () => {
      setIsPlaying(false);
      setShowCenterPlay(true);
    };

    video.addEventListener('timeupdate', handleTimeUpdate);
    video.addEventListener('durationchange', handleDurationChange);
    video.addEventListener('play', handlePlay);
    video.addEventListener('pause', handlePause);
    video.addEventListener('loadstart', handleLoadStart);
    video.addEventListener('canplay', handleCanPlay);
    video.addEventListener('waiting', handleWaiting);
    video.addEventListener('playing', handlePlaying);
    video.addEventListener('volumechange', handleVolumeChange);
    video.addEventListener('ratechange', handleRateChange);
    video.addEventListener('ended', handleEnded);

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate);
      video.removeEventListener('durationchange', handleDurationChange);
      video.removeEventListener('play', handlePlay);
      video.removeEventListener('pause', handlePause);
      video.removeEventListener('loadstart', handleLoadStart);
      video.removeEventListener('canplay', handleCanPlay);
      video.removeEventListener('waiting', handleWaiting);
      video.removeEventListener('playing', handlePlaying);
      video.removeEventListener('volumechange', handleVolumeChange);
      video.removeEventListener('ratechange', handleRateChange);
      video.removeEventListener('ended', handleEnded);
    };
  }, []);

  // Update buffered amount
  const updateBuffered = () => {
    const video = videoRef.current;
    if (!video || !video.buffered.length) return;
    
    const bufferedEnd = video.buffered.end(video.buffered.length - 1);
    const bufferedPercent = (bufferedEnd / video.duration) * 100;
    setBuffered(bufferedPercent);
  };

  // Controls visibility
  const resetControlsTimeout = useCallback(() => {
    if (controlsTimeoutRef.current) {
      clearTimeout(controlsTimeoutRef.current);
    }
    setIsControlsVisible(true);

    // На мобильных не скрываем контролы, если видео на паузе
    if (!isMobile() && isPlaying && hasInteracted) {
      controlsTimeoutRef.current = window.setTimeout(() => {
        setIsControlsVisible(false);
        setIsRateMenuOpen(false);
        setShowVolumeSlider(false);
      }, 3000);
    }
  }, [isPlaying, hasInteracted]);

  useEffect(() => {
    resetControlsTimeout();
  }, [resetControlsTimeout]);

  // Playback control
  const togglePlay = () => {
    if (!videoRef.current) return;
    setHasInteracted(true);
    
    if (isPlaying) {
      videoRef.current.pause();
    } else {
      videoRef.current.play();
    }
  };

  // Volume control
  const handleVolumeChange = (newVolume: number) => {
    if (videoRef.current) {
      videoRef.current.volume = newVolume;
      setVolume(newVolume);
      if (newVolume > 0) {
        setPreviousVolume(newVolume);
      }
    }
  };

  const toggleMute = () => {
    if (volume > 0) {
      handleVolumeChange(0);
    } else {
      handleVolumeChange(previousVolume);
    }
  };

  // Playback rate
  const changePlaybackRate = (rate: number) => {
    if (videoRef.current) {
      videoRef.current.playbackRate = rate;
      setPlaybackRate(rate);
      setIsRateMenuOpen(false);
    }
  };

  // Seeking
  const handleSeek = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!progressRef.current || !videoRef.current) return;
    
    const rect = progressRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = x / rect.width;
    const newTime = percentage * duration;
    
    videoRef.current.currentTime = newTime;
    setIsSeeking(false);
    setSeekTime(null);
  };

  const handleSeekPreview = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!progressRef.current || !duration || isMobile()) return;
    
    const rect = progressRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = Math.max(0, Math.min(1, x / rect.width));
    const time = percentage * duration;
    
    setSeekTime(time);
    setTooltipPosition(x);
  };

  // Skip functions
  const skip = (seconds: number) => {
    if (!videoRef.current) return;
    videoRef.current.currentTime = Math.max(0, Math.min(duration, videoRef.current.currentTime + seconds));
  };

  // Fullscreen
  const toggleFullscreen = () => {
    if (!containerRef.current) return;

    if (!document.fullscreenElement) {
      containerRef.current.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  // Format time
  const formatTime = (seconds: number) => {
    if (isNaN(seconds)) return '0:00';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  // Volume slider visibility
  const handleVolumeHover = () => {
    if (volumeHideTimeoutRef.current) {
      clearTimeout(volumeHideTimeoutRef.current);
    }
    setShowVolumeSlider(true);
  };

  const handleVolumeLeave = () => {
    volumeHideTimeoutRef.current = window.setTimeout(() => {
      setShowVolumeSlider(false);
    }, 1500);
  };

  if (error) {
    return (
      <div className={`video-player-error ${className}`} style={styles.errorContainer}>
        <div style={styles.errorContent}>
          <p style={styles.errorText}>⚠️ {error}</p>
          <button 
            onClick={() => window.location.reload()} 
            style={styles.errorButton}
          >
            Попробовать снова
          </button>
        </div>
      </div>
    );
  }

  const mobile = isMobile();

  return (
    <div 
      ref={containerRef}
      className={`video-player-container ${className}`}
      style={styles.container}
      onMouseMove={resetControlsTimeout}
      onMouseLeave={() => {
        if (!mobile) setIsControlsVisible(false);
        setSeekTime(null);
      }}
    >
<video
  ref={videoRef}
  poster={poster}
  style={styles.video}
  playsInline
  disablePictureInPicture
  controlsList="nodownload"
  onContextMenu={e => e.preventDefault()}
  onError={() => {
    setIsLoading(false);
    setIsBuffering(false);

    const video = videoRef.current;
    let message = 'Не удалось загрузить видео';
    if (video?.error) {
      switch (video.error.code) {
        case video.error.MEDIA_ERR_ABORTED:
          message = 'Загрузка видео была отменена пользователем.';
          break;
        case video.error.MEDIA_ERR_NETWORK:
          message = 'Ошибка сети при загрузке видео.';
          break;
        case video.error.MEDIA_ERR_DECODE:
          message = 'Ошибка декодирования: видео повреждено или формат не поддерживается.';
          break;
        case video.error.MEDIA_ERR_SRC_NOT_SUPPORTED:
          message = 'Видео не найдено или не поддерживается.';
          break;
        default:
          message = 'Не удалось загрузить видео.';
      }
    }
    setError(message);    // Показываем ошибку в твоём UI
    onError(message);      // Вызываем внешний обработчик (если передан через пропсы)
  }}
/>

      
      {/* Click overlay */}
      <div
        style={{
          position: 'absolute',
          top: 0, left: 0, right: 0, bottom: 0,
          zIndex: 4,
          cursor: 'pointer',
          background: 'transparent'
        }}
        onClick={() => {
          togglePlay();
          setIsControlsVisible(true);
        }}
      />

      {/* Center play button */}
      {showCenterPlay && !isLoading && (
        <div className="center-play-container" style={styles.centerPlayContainer} onClick={togglePlay}>
          <PlayCircle size={mobile ? 60 : 80} style={styles.centerPlayIcon} />
        </div>
      )}

      {/* Loading indicator */}
      {(isLoading || isBuffering) && (
        <div style={styles.loadingContainer}>
          <Loader size={mobile ? 36 : 48} style={styles.loadingSpinner} />
        </div>
      )}

      {/* Skip indicators - only on desktop */}
      {!mobile && (
        <div style={styles.skipContainer}>
          <div 
            style={styles.skipLeft} 
            onDoubleClick={(e) => {
              e.stopPropagation();
              skip(-10);
            }}
          />
          <div 
            style={styles.skipRight}
            onDoubleClick={(e) => {
              e.stopPropagation();
              skip(10);
            }}
          />
        </div>
      )}

      {/* Controls */}
      <div style={{
        ...styles.controls,
        ...(mobile ? styles.controlsMobile : {}),
        opacity: (isControlsVisible || !isPlaying) ? 1 : 0,
        pointerEvents: (isControlsVisible || !isPlaying) ? 'auto' : 'none'
      }}>
        {/* Progress bar */}
        <div 
          ref={progressRef}
          className="progress-container"
          style={{
            ...styles.progressContainer,
            ...(mobile ? styles.progressContainerMobile : {})
          }}
          onMouseMove={handleSeekPreview}
          onMouseLeave={() => setSeekTime(null)}
          onClick={handleSeek}
        >
          {/* Buffered */}
          <div style={{
            ...styles.progressBuffered,
            width: `${buffered}%`
          }} />
          
          {/* Progress */}
          <div style={{
            ...styles.progressFilled,
            width: `${(currentTime / duration) * 100}%`
          }} />
          
          {/* Seek preview - only on desktop */}
          {!mobile && seekTime !== null && (
            <div style={{
              ...styles.seekTooltip,
              left: `${tooltipPosition}px`
            }}>
              {formatTime(seekTime)}
            </div>
          )}
          
          {/* Scrubber */}
          <div className="progress-scrubber" style={{
            ...styles.progressScrubber,
            ...(mobile ? styles.progressScrubberMobile : {}),
            left: `${(currentTime / duration) * 100}%`
          }} />
        </div>

{/* Control buttons */}
<div style={styles.controlsRow}>
  {/* -------- ЛЕВО -------- */}
  <div style={styles.controlsLeft}>
    {/* ▶︎ / ❚❚ */}
    <button onClick={togglePlay} style={styles.controlButton}>
      {isPlaying ? <Pause size={20}/> : <Play size={20}/>}
    </button>

    {/* Volume + всплывающий слайдер */}
    <div style={styles.volumeContainer}
         onMouseEnter={handleVolumeHover}
         onMouseLeave={handleVolumeLeave}>
      <button onClick={toggleMute} style={styles.controlButton}>
        {volume === 0 ? <VolumeX size={20}/> : <Volume2 size={20}/> }
      </button>

      {/* слайдер выезжает при hover */}
      <div style={{
        ...styles.volumeSliderContainer,
        opacity: showVolumeSlider ? 1 : 0,
        pointerEvents: showVolumeSlider ? 'auto' : 'none'
      }}>
        <input type="range" min={0} max={1} step={0.01}
               value={volume}
               onChange={e => handleVolumeChange(+e.target.value)}
               style={styles.volumeSlider}/>
      </div>
    </div>

    {/* Текущее время / длительность */}
    <div style={styles.timeDisplay}>
      {formatTime(currentTime)} / {formatTime(duration)}
    </div>
  </div>

  {/* -------- ПРАВО -------- */}
  <div style={styles.controlsRight}>
    {/* ⚙︎ — меню со скоростью, качество можно добавить позже */}
    <div style={styles.menuContainer}>
      <button onClick={() => setIsRateMenuOpen(!isRateMenuOpen)}
              style={styles.controlButton}>
        ⚙︎
      </button>

      {isRateMenuOpen && (
        <div style={styles.menu}>
          {[0.25,0.5,0.75,1,1.25,1.5,1.75,2].map(r => (
            <div key={r}
                 className="menu-item"
                 style={{
                   ...styles.menuItem,
                   ...(playbackRate===r ? styles.menuItemActive : {})
                 }}
                 onClick={()=>changePlaybackRate(r)}>
              {r}×
            </div>
          ))}
        </div>
      )}
    </div>

    {/* ⛶ / ▭ — полноэкранный режим */}
    <button onClick={toggleFullscreen} style={styles.controlButton}>
      {isFullscreen ? <Minimize size={20}/> : <Maximize size={20}/> }
    </button>
  </div>
</div>

      </div>
    </div>
  );

  
};

// Styles
const styles: { [key: string]: React.CSSProperties } = {
  container: {
    position: 'relative',
    width: '100%',
    backgroundColor: '#000',
    borderRadius: '8px',
    overflow: 'hidden',
    aspectRatio: '16 / 9',
    cursor: 'default',
    userSelect: 'none'
  },
  video: {
    width: '100%',
    height: '100%',
    display: 'block',
    objectFit: 'contain'
  },
  centerPlayContainer: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    cursor: 'pointer',
    zIndex: 5,
    transition: 'transform 0.2s'
  },
  centerPlayIcon: {
    color: '#fff',
    filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.5))',
    transition: 'transform 0.2s'
  },
  loadingContainer: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    zIndex: 10
  },
  loadingSpinner: {
    color: '#fff',
    animation: 'spin 1s linear infinite'
  },
  skipContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    display: 'flex',
    pointerEvents: 'none'
  },
  skipLeft: {
    flex: 1,
    pointerEvents: 'auto',
    cursor: 'pointer'
  },
  skipRight: {
    flex: 1,
    pointerEvents: 'auto',
    cursor: 'pointer'
  },
  controls: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    width: '100%',
    background: 'linear-gradient(to top, rgba(0,0,0,0.7), transparent)',
    padding: '20px 16px 16px',
    transition: 'opacity 0.3s',
    zIndex: 20
  },
  controlsMobile: {
    padding: '16px 12px 12px'
  },
  progressContainer: {
    position: 'relative',
    width: '100%',
    height: '5px',
    backgroundColor: 'rgba(255,255,255,0.3)',
    borderRadius: '2.5px',
    cursor: 'pointer',
    marginBottom: '16px',
    transition: 'height 0.15s'
  },
  progressContainerMobile: {
    height: '4px',
    marginBottom: '12px'
  },
  progressBuffered: {
    position: 'absolute',
    top: 0,
    left: 0,
    height: '100%',
    backgroundColor: 'rgba(255,255,255,0.4)',
    borderRadius: '2.5px'
  },
  progressFilled: {
    position: 'absolute',
    top: 0,
    left: 0,
    height: '100%',
    backgroundColor: '#0091ff65',
    borderRadius: '2.5px',
    transition: 'width 0.3s cubic-bezier(0.6, 0.3, 0.5, 1)'
  },
  progressScrubber: {
    position: 'absolute',
    top: '50%',
    width: '12px',
    height: '12px',
    backgroundColor: '#0077ffaf',
    borderRadius: '50%',
    transform: 'translate(-50%, -50%)',
    transition: 'left 0.3s cubic-bezier(0.6, 0.3, 0.5, 1), width 0.15s, height 0.15s'
  },
  progressScrubberMobile: {
    width: '10px',
    height: '10px'
  },
  seekTooltip: {
    position: 'absolute',
    bottom: '20px',
    transform: 'translateX(-50%)',
    backgroundColor: 'rgba(0,0,0,0.8)',
    color: '#fff',
    padding: '4px 8px',
    borderRadius: '4px',
    fontSize: '12px',
    pointerEvents: 'none',
    whiteSpace: 'nowrap'
  },
  controlsRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: '8px'
  },
  controlsLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px'
  },
  controlsRight: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px'
  },
  controlButton: {
    background: 'none',
    border: 'none',
    color: '#fff',
    cursor: 'pointer',
    padding: '8px',
    borderRadius: '4px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'background-color 0.2s',
    fontSize: '14px',
    fontWeight: '500'
  },
  controlButtonMobile: {
    padding: '6px'
  },
  volumeContainer: {
    display: 'flex',
    alignItems: 'center',
    position: 'relative'
  },
  volumeSliderContainer: {
    position: 'absolute',
    left: '100%',
    top: '50%',
    transform: 'translateY(-50%)',
    marginLeft: '8px',
    transition: 'opacity 0.2s',
    background: 'rgba(0,0,0,0.8)',
    padding: '4px 12px',
    borderRadius: '4px'
  },
  volumeSlider: {
    width: '80px',
    height: '4px',
    appearance: 'none' as any,
    backgroundColor: 'rgba(255,255,255,0.3)',
    outline: 'none',
    borderRadius: '2px',
    cursor: 'pointer'
  },
  timeDisplay: {
    color: '#fff',
    fontSize: '14px',
    fontFamily: 'monospace',
    marginLeft: '8px',
    userSelect: 'none'
  },
  timeDisplayMobile: {
    fontSize: '12px',
    marginLeft: '4px'
  },
  menuContainer: {
    position: 'relative'
  },
  menu: {
    position: 'absolute',
    bottom: '100%',
    right: 0,
    marginBottom: '8px',
    backgroundColor: 'rgba(28,28,28,0.95)',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: '8px',
    padding: '8px 0',
    minWidth: '120px',
    maxHeight: '300px',
    overflowY: 'auto',
    zIndex: 100
  },
  menuItem: {
    padding: '8px 16px',
    color: '#fff',
    fontSize: '14px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
    whiteSpace: 'nowrap'
  },
  menuItemActive: {
    backgroundColor: 'rgba(255,255,255,0.1)',
    color: '#0095ffff'
  },
  errorContainer: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '400px',
    backgroundColor: '#f8f9fa',
    borderRadius: '8px',
    border: '1px solid #dee2e6'
  },
  errorContent: {
    textAlign: 'center' as const,
    padding: '20px'
  },
  errorText: {
    color: '#6c757d',
    fontSize: '16px',
    marginBottom: '16px'
  },
  errorButton: {
    padding: '10px 20px',
    backgroundColor: '#007bff',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
    transition: 'background-color 0.2s'
  },

};

export default VideoPlayer;