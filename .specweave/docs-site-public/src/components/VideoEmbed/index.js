import React, { useState } from 'react';
import styles from './VideoEmbed.module.css';

const CHAPTERS = [
  { time: '0:00', seconds: 0, title: 'Introduction' },
  { time: '0:11', seconds: 11, title: 'Setup & Init' },
  { time: '0:41', seconds: 41, title: 'Feature Request' },
  { time: '0:57', seconds: 57, title: 'PM Questionnaire' },
  { time: '1:22', seconds: 82, title: 'Reviewing Specs' },
  { time: '1:58', seconds: 118, title: 'Implementation' },
  { time: '2:32', seconds: 152, title: 'Testing & Grill' },
  { time: '2:49', seconds: 169, title: 'Completion' },
  { time: '2:54', seconds: 174, title: 'Live Demo' },
];

const TRANSCRIPT = [
  { time: '0:00', text: 'Demonstrating SpecWeave development workflow with OpenCode, which is a non-cloud AI tool.' },
  { time: '0:11', text: 'Doing SpecWeave init, setting English, non-cloud tool, choosing OpenCode, and starting from scratch. We have our skills loaded, but they are not active by default here, so we have to reload and restart OpenCode. Now we can see that the increment skill is available.' },
  { time: '0:41', text: 'Create a web calculator with a backend. We could see that the whole skill definition is loaded into the main agent context. Then we could follow the next steps.' },
  { time: '0:57', text: 'This is a kind of questionnaire. What operations should the calculator support? Let\'s start with the basic. Next. What backend stack do you prefer? Node.js should be fine. Frontend style for the calculator UI. We\'re using MiniMax M2.5 free model.' },
  { time: '1:22', text: 'Let\'s take a look at the .specweave folder. Here we go. This is the first increment that is already created. We have metadata.json, spec file defining our user stories. For now, it\'s still the template. You could see that this is in progress. Now we could see that the spec file is ready.' },
  { time: '1:58', text: 'Now let\'s implement the increment. We could call command /do, or just simply say something like "implement the first increment."' },
  { time: '2:24', text: 'We could see that it goes through each task. This is the start of our implementation. Runs tests including end-to-end. Grills the implementation. Runs all tests again. And completes the increment.' },
  { time: '2:49', text: 'All acceptance criteria are completed now.' },
  { time: '2:54', text: 'Let\'s run the server. Simple web calculator is implemented.' },
];

export default function VideoEmbed({
  videoId = 'WVwyqsHS8dc',
  version = '1.0.519',
}) {
  const [transcriptOpen, setTranscriptOpen] = useState(false);

  const youtubeUrl = `https://www.youtube.com/watch?v=${videoId}`;
  const embedUrl = `https://www.youtube.com/embed/${videoId}`;

  return (
    <div className={styles.wrapper}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.topRow}>
          <span className={styles.badge}>SpecWeave v{version}</span>
          <span className={styles.duration}>3:52</span>
        </div>
        <h2 className={styles.title}>
          SpecWeave + <span>OpenCode</span>
        </h2>
        <p className={styles.subtitle}>
          Build a web calculator with Node.js backend in 4 minutes.
          Non-cloud AI. No API keys. Full spec-driven lifecycle.
        </p>
      </div>

      {/* Video */}
      <div className={styles.videoSection}>
        <div className={styles.videoFrame}>
          <div className={styles.videoAspect}>
            <iframe
              src={embedUrl}
              title="SpecWeave + OpenCode: Build a Web Calculator in 4 Minutes"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              referrerPolicy="strict-origin-when-cross-origin"
              allowFullScreen
              loading="lazy"
            />
          </div>
        </div>
      </div>

      {/* Chapter Timeline */}
      <div className={styles.chapters}>
        <div className={styles.chaptersLabel}>Chapters</div>
        <div className={styles.timeline}>
          {CHAPTERS.map((ch, i) => (
            <a
              key={i}
              className={`${styles.chapter} ${i === 0 ? styles.chapterActive : ''}`}
              href={`${youtubeUrl}&t=${ch.seconds}s`}
              target="_blank"
              rel="noopener noreferrer"
            >
              <div className={styles.chapterTime}>{ch.time}</div>
              <div className={styles.chapterTitle}>{ch.title}</div>
            </a>
          ))}
        </div>
      </div>

      {/* Transcript */}
      <div className={styles.transcriptSection}>
        <button
          className={styles.transcriptToggle}
          onClick={() => setTranscriptOpen(!transcriptOpen)}
          aria-expanded={transcriptOpen}
        >
          <span>Transcript</span>
          <span className={`${styles.transcriptArrow} ${transcriptOpen ? styles.transcriptArrowOpen : ''}`}>
            &#9660;
          </span>
        </button>
        <div className={`${styles.transcriptBody} ${transcriptOpen ? styles.transcriptBodyOpen : ''}`}>
          <div className={styles.transcriptInner}>
            {TRANSCRIPT.map((line, i) => (
              <div key={i} className={styles.transcriptLine}>
                <span className={styles.transcriptTimestamp}>{line.time}</span>
                <span className={styles.transcriptText}>{line.text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className={styles.footer}>
        <div className={styles.footerLeft}>
          <span className={styles.channelName}>
            <a href="https://www.youtube.com/@AntonAbyzovAIPower" target="_blank" rel="noopener noreferrer">
              Anton Abyzov AI Power
            </a>
          </span>
          <span className={styles.subtitleNotice}>
            Auto-translated subtitles available
          </span>
        </div>
        <a
          className={styles.watchButton}
          href={youtubeUrl}
          target="_blank"
          rel="noopener noreferrer"
        >
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M10 15l5.19-3L10 9v6m11.56-7.83c.13.47.22 1.1.28 1.9.07.8.1 1.49.1 2.09L22 12c0 2.19-.16 3.8-.44 4.83-.25.9-.83 1.48-1.73 1.73-.47.13-1.33.22-2.65.28-1.3.07-2.49.1-3.59.1L12 19c-4.19 0-6.8-.16-7.83-.44-.9-.25-1.48-.83-1.73-1.73-.13-.47-.22-1.1-.28-1.9-.07-.8-.1-1.49-.1-2.09L2 12c0-2.19.16-3.8.44-4.83.25-.9.83-1.48 1.73-1.73.47-.13 1.33-.22 2.65-.28 1.3-.07 2.49-.1 3.59-.1L12 5c4.19 0 6.8.16 7.83.44.9.25 1.48.83 1.73 1.73z"/>
          </svg>
          Watch on YouTube
        </a>
      </div>
    </div>
  );
}
