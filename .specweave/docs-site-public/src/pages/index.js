import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero', styles.heroBanner)}>
      <div className="container">
        <h1 className={styles.heroTitle}><span className={styles.brandName}>specweave</span>{' '}<span className={styles.heroWord}>Documentation</span></h1>
        <p className={styles.heroSubtitle}>{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--primary button--lg"
            to="/academy">
            Browse Documentation
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={siteConfig.title}
      description="Project Documentation">
      <HomepageHeader />
      <main>
        <div className="container" style={{padding: '3rem 0'}}>
          <div className={styles.categoryGrid}>
          <Link to="/academy" className={styles.categoryCard} key="academy">
            <span className={styles.categoryIcon}>📂</span>
            <h3>Academy</h3>
            <p>Academy documentation</p>
            <span className={styles.docCount}>6 documents</span>
          </Link>
          <Link to="/api" className={styles.categoryCard} key="api">
            <span className={styles.categoryIcon}>🔗</span>
            <h3>API</h3>
            <p>API reference and endpoints</p>
            <span className={styles.docCount}>1 document</span>
          </Link>
          <Link to="/commands" className={styles.categoryCard} key="commands">
            <span className={styles.categoryIcon}>📂</span>
            <h3>Commands</h3>
            <p>Commands documentation</p>
            <span className={styles.docCount}>12 documents</span>
          </Link>
          <Link to="/development" className={styles.categoryCard} key="development">
            <span className={styles.categoryIcon}>📂</span>
            <h3>Development</h3>
            <p>Development documentation</p>
            <span className={styles.docCount}>2 documents</span>
          </Link>
          <Link to="/glossary" className={styles.categoryCard} key="glossary">
            <span className={styles.categoryIcon}>📂</span>
            <h3>Glossary</h3>
            <p>Glossary documentation</p>
            <span className={styles.docCount}>70 documents</span>
          </Link>
          <Link to="/guides" className={styles.categoryCard} key="guides">
            <span className={styles.categoryIcon}>📖</span>
            <h3>Guides</h3>
            <p>How-to guides and tutorials</p>
            <span className={styles.docCount}>49 documents</span>
          </Link>
          <Link to="/integrations" className={styles.categoryCard} key="integrations">
            <span className={styles.categoryIcon}>📂</span>
            <h3>Integrations</h3>
            <p>Integrations documentation</p>
            <span className={styles.docCount}>3 documents</span>
          </Link>
          <Link to="/learn" className={styles.categoryCard} key="learn">
            <span className={styles.categoryIcon}>📂</span>
            <h3>Learn</h3>
            <p>Learn documentation</p>
            <span className={styles.docCount}>11 documents</span>
          </Link>
          <Link to="/marketing" className={styles.categoryCard} key="marketing">
            <span className={styles.categoryIcon}>📂</span>
            <h3>Marketing</h3>
            <p>Marketing documentation</p>
            <span className={styles.docCount}>5 documents</span>
          </Link>
          <Link to="/overview" className={styles.categoryCard} key="overview">
            <span className={styles.categoryIcon}>📂</span>
            <h3>Overview</h3>
            <p>Overview documentation</p>
            <span className={styles.docCount}>5 documents</span>
          </Link>
          <Link to="/reference" className={styles.categoryCard} key="reference">
            <span className={styles.categoryIcon}>📂</span>
            <h3>Reference</h3>
            <p>Reference documentation</p>
            <span className={styles.docCount}>2 documents</span>
          </Link>
          <Link to="/scripts" className={styles.categoryCard} key="scripts">
            <span className={styles.categoryIcon}>📂</span>
            <h3>Scripts</h3>
            <p>Scripts documentation</p>
            <span className={styles.docCount}>5 documents</span>
          </Link>
          <Link to="/troubleshooting" className={styles.categoryCard} key="troubleshooting">
            <span className={styles.categoryIcon}>🔧</span>
            <h3>Troubleshooting</h3>
            <p>Debugging guides and known issues</p>
            <span className={styles.docCount}>9 documents</span>
          </Link>
          <Link to="/workflows" className={styles.categoryCard} key="workflows">
            <span className={styles.categoryIcon}>📂</span>
            <h3>Workflows</h3>
            <p>Workflows documentation</p>
            <span className={styles.docCount}>5 documents</span>
          </Link>
          </div>
        </div>
      </main>
    </Layout>
  );
}
