import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const PptxGenJS = require('/Users/antonabyzov/.nvm/versions/node/v22.20.0/lib/node_modules/pptxgenjs/dist/pptxgen.cjs.js');

const pptx = new PptxGenJS();
pptx.layout = 'LAYOUT_16x9';
pptx.author = 'EasyChamp, Inc.';
pptx.title = 'Street Champ — PlayStation 5 Project Pitch';

const SW = 10, SH = 5.625;
const TOTAL = 11;

// ── Paths ──
const IMG = '/Users/antonabyzov/Projects/github/specweave-umb/tools/concept-art';
const gameplayImg = `${IMG}/gameplay-scene.jpg`;
const courtImg = `${IMG}/court-environment.jpg`;
const charImg = `${IMG}/character-lineup.jpg`;
const logoIcon = `${IMG}/ec-logo-icon.png`;
const logoLabel = `${IMG}/ec-logo-label.png`;

// ── Colors ──
const C = {
  bg: '0A0E27', card: '141A42', blue: '2D7FF9', gold: 'D4A843',
  white: 'FFFFFF', body: 'D0D8EC', gray: '8B93B0', darkBlue: '1A2158',
};

// ── Helpers ──
function addBg(s) { s.background = { color: C.bg }; }
function addFooter(s, n) {
  s.addText(`${n} / ${TOTAL}`, { x: 4.3, y: 5.05, w: 1.4, h: 0.25, fontSize: 8, color: C.gray, fontFace: 'Calibri', align: 'center' });
}
function addBar(s) { s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 0.07, h: SH, fill: { color: C.blue } }); }
function addLabel(s, t, x = 0.6, y = 0.3) {
  s.addText(t.toUpperCase(), { x, y, w: 3, h: 0.22, fontSize: 9, fontFace: 'Calibri', color: C.gold, bold: true, letterSpacing: 3, margin: 0 });
}

// ═══════════════ SLIDE 1 — COVER (gameplay background) ═══════════════
{
  const s = pptx.addSlide();
  // Gameplay screenshot as full-bleed background
  s.addImage({ path: gameplayImg, x: 0, y: 0, w: SW, h: SH });
  // Dark overlay for text readability
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: SW, h: SH, fill: { color: '000000', transparency: 35 } });
  // Gradient overlay on left side for text area
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 5.5, h: SH, fill: { color: C.bg, transparency: 15 } });

  // EasyChamp logo icon (top-left)
  s.addImage({ path: logoIcon, x: 0.6, y: 0.4, w: 0.4, h: 0.46 });

  // Title
  s.addText('STREET\nCHAMP', {
    x: 0.6, y: 1.2, w: 5, h: 2.0,
    fontSize: 64, fontFace: 'Arial Black', color: C.white, bold: true,
    lineSpacingMultiple: 0.85, margin: 0, shadow: { type: 'outer', blur: 10, offset: 3, color: '000000', opacity: 0.6 },
  });

  s.addText('Project Pitch  —  PlayStation 5', {
    x: 0.6, y: 3.2, w: 5, h: 0.35,
    fontSize: 16, fontFace: 'Calibri', color: C.white,
    shadow: { type: 'outer', blur: 6, offset: 2, color: '000000', opacity: 0.5 },
  });

  s.addText('April 2026', {
    x: 0.6, y: 3.6, w: 3, h: 0.25,
    fontSize: 11, fontFace: 'Calibri', color: C.body,
  });

  // Bottom bar
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 4.75, w: SW, h: 0.6, fill: { color: C.darkBlue, transparency: 20 } });
  s.addText('EASYCHAMP, INC.', {
    x: 0.6, y: 4.8, w: 4, h: 0.45,
    fontSize: 12, fontFace: 'Calibri', color: C.gold, bold: true, letterSpacing: 4, valign: 'middle',
  });
  s.addText('easychamp.com', {
    x: 7.0, y: 4.8, w: 2.5, h: 0.45,
    fontSize: 11, fontFace: 'Calibri', color: C.body, align: 'right', valign: 'middle',
  });
}

// ═══════════════ SLIDE 2 — CONCEPT OVERVIEW ═══════════════
{
  const s = pptx.addSlide();
  addBg(s); addBar(s); addLabel(s, 'Concept Overview'); addFooter(s, 2);

  s.addText('The Game', {
    x: 0.6, y: 0.6, w: 8, h: 0.55,
    fontSize: 36, fontFace: 'Arial Black', color: C.white, bold: true, margin: 0,
  });

  s.addShape(pptx.ShapeType.rect, { x: 0.6, y: 1.4, w: 8.8, h: 1.5, fill: { color: C.card }, rectRadius: 0.08 });
  s.addText(
    'Street Champ is a fast-paced, arcade-style 3v3 street football game built for PS5. ' +
    'Players assemble crews, master trick moves, and compete in iconic urban courts worldwide. ' +
    'Think FIFA Street meets modern indie craft \u2014 tight controls, expressive animations, ' +
    'and addictive online competition.',
    { x: 0.9, y: 1.55, w: 8.2, h: 1.2, fontSize: 14, fontFace: 'Calibri', color: C.body, lineSpacingMultiple: 1.4 }
  );

  const stats = [
    { num: '3v3', label: 'Players per side' },
    { num: '8+', label: 'Urban courts worldwide' },
    { num: '50+', label: 'Trick moves to master' },
  ];
  stats.forEach((st, i) => {
    const x = 0.6 + i * 3.05;
    s.addShape(pptx.ShapeType.rect, { x, y: 3.2, w: 2.75, h: 1.5, fill: { color: C.card }, rectRadius: 0.08 });
    s.addText(st.num, { x, y: 3.3, w: 2.75, h: 0.75, fontSize: 32, fontFace: 'Arial Black', color: C.white, align: 'center', bold: true, margin: 0 });
    s.addText(st.label, { x, y: 4.05, w: 2.75, h: 0.4, fontSize: 11, fontFace: 'Calibri', color: C.gray, align: 'center' });
  });
}

// ═══════════════ SLIDE 3 — TARGET PLATFORM ═══════════════
{
  const s = pptx.addSlide();
  addBg(s); addBar(s); addLabel(s, 'Target Platform'); addFooter(s, 3);

  s.addText('Built for PlayStation 5', {
    x: 0.6, y: 0.6, w: 8, h: 0.55,
    fontSize: 34, fontFace: 'Arial Black', color: C.white, bold: true, margin: 0,
  });

  // PS5 features card
  s.addShape(pptx.ShapeType.rect, { x: 0.6, y: 1.4, w: 4.3, h: 3.5, fill: { color: C.card }, rectRadius: 0.08 });
  s.addText('PRIMARY PLATFORM', { x: 0.9, y: 1.55, w: 2.5, h: 0.2, fontSize: 9, fontFace: 'Calibri', color: C.gold, bold: true, letterSpacing: 2, margin: 0 });

  const ps5 = [
    ['DualSense Haptics', 'Feel every touch, tackle, and trick'],
    ['Adaptive Triggers', 'Variable resistance for power shots'],
    ['SSD Streaming', 'Instant court loading, zero wait'],
    ['3D Audio', 'Tempest-powered crowd and ball acoustics'],
  ];
  ps5.forEach((f, i) => {
    const y = 2.0 + i * 0.65;
    s.addShape(pptx.ShapeType.ellipse, { x: 0.9, y: y + 0.05, w: 0.15, h: 0.15, fill: { color: C.blue } });
    s.addText(f[0], { x: 1.2, y: y - 0.05, w: 3.4, h: 0.25, fontSize: 12, fontFace: 'Calibri', color: C.white, bold: true, margin: 0 });
    s.addText(f[1], { x: 1.2, y: y + 0.2, w: 3.4, h: 0.25, fontSize: 10, fontFace: 'Calibri', color: C.gray, margin: 0 });
  });

  // Engine card
  s.addShape(pptx.ShapeType.rect, { x: 5.1, y: 1.4, w: 4.3, h: 1.5, fill: { color: C.card }, rectRadius: 0.08 });
  s.addText('ENGINE', { x: 5.4, y: 1.55, w: 2, h: 0.2, fontSize: 9, fontFace: 'Calibri', color: C.gold, bold: true, letterSpacing: 2, margin: 0 });
  s.addText('Unreal Engine 5', { x: 5.4, y: 1.9, w: 3.7, h: 0.4, fontSize: 22, fontFace: 'Arial Black', color: C.white, bold: true, margin: 0 });
  s.addText('Nanite, Lumen, MetaHuman pipeline', { x: 5.4, y: 2.35, w: 3.7, h: 0.3, fontSize: 11, fontFace: 'Calibri', color: C.gray });

  // PS4 stretch
  s.addShape(pptx.ShapeType.rect, { x: 5.1, y: 3.1, w: 4.3, h: 1.8, fill: { color: C.darkBlue }, rectRadius: 0.08 });
  s.addText('STRETCH GOAL', { x: 5.4, y: 3.25, w: 2, h: 0.2, fontSize: 9, fontFace: 'Calibri', color: C.gold, bold: true, letterSpacing: 2, margin: 0 });
  s.addText('PlayStation 4', { x: 5.4, y: 3.55, w: 3.7, h: 0.35, fontSize: 18, fontFace: 'Arial Black', color: C.body, bold: true, margin: 0 });
  s.addText('Scaled-down visuals, same core gameplay.\n110M+ installed base.', { x: 5.4, y: 4.0, w: 3.7, h: 0.65, fontSize: 11, fontFace: 'Calibri', color: C.gray, lineSpacingMultiple: 1.3 });
}

// ═══════════════ SLIDE 4 — APPEAL ═══════════════
{
  const s = pptx.addSlide();
  addBg(s); addBar(s); addLabel(s, 'Appeal'); addFooter(s, 4);

  s.addText('Gameplay & Genre', { x: 0.6, y: 0.6, w: 8, h: 0.5, fontSize: 34, fontFace: 'Arial Black', color: C.white, bold: true, margin: 0 });
  s.addText('Arcade Sports  /  Multiplayer', { x: 0.6, y: 1.15, w: 4, h: 0.25, fontSize: 12, fontFace: 'Calibri', color: C.blue });

  s.addText('CORE LOOP', { x: 0.6, y: 1.6, w: 2, h: 0.2, fontSize: 9, fontFace: 'Calibri', color: C.gold, bold: true, letterSpacing: 2, margin: 0 });
  const loop = ['Pick Crew', 'Enter Match', 'Score with Style', 'Earn Rep', 'Unlock'];
  loop.forEach((step, i) => {
    const x = 0.6 + i * 1.82;
    s.addShape(pptx.ShapeType.rect, { x, y: 1.9, w: 1.6, h: 0.5, fill: { color: i === 2 ? C.blue : C.card }, rectRadius: 0.05 });
    s.addText(step, { x, y: 1.9, w: 1.6, h: 0.5, fontSize: 10, fontFace: 'Calibri', color: i === 2 ? C.bg : C.body, bold: true, align: 'center', valign: 'middle' });
    if (i < 4) s.addText('\u25B6', { x: x + 1.6, y: 1.9, w: 0.22, h: 0.5, fontSize: 8, color: C.gray, align: 'center', valign: 'middle' });
  });

  s.addText('KEY DIFFERENTIATORS', { x: 0.6, y: 2.65, w: 3, h: 0.2, fontSize: 9, fontFace: 'Calibri', color: C.gold, bold: true, letterSpacing: 2, margin: 0 });
  const diffs = [
    { n: '01', t: 'Trick System', d: 'Flashy moves boost your score multiplier \u2014 but can be intercepted. High risk, high reward.' },
    { n: '02', t: 'Crew Chemistry', d: 'Teammates who play together develop unique combo moves and synergies over time.' },
    { n: '03', t: 'Court Hazards', d: 'Each venue has unique elements \u2014 puddles, walls for ricochets, spectator distractions.' },
  ];
  diffs.forEach((d, i) => {
    const x = 0.6 + i * 3.05;
    s.addShape(pptx.ShapeType.rect, { x, y: 3.0, w: 2.75, h: 2.0, fill: { color: C.card }, rectRadius: 0.08 });
    s.addText(d.n, { x: x + 0.2, y: 3.1, w: 0.5, h: 0.35, fontSize: 20, fontFace: 'Arial Black', color: C.blue, bold: true, margin: 0 });
    s.addText(d.t, { x: x + 0.2, y: 3.5, w: 2.3, h: 0.3, fontSize: 14, fontFace: 'Calibri', color: C.white, bold: true, margin: 0 });
    s.addText(d.d, { x: x + 0.2, y: 3.85, w: 2.3, h: 0.95, fontSize: 10, fontFace: 'Calibri', color: C.gray, lineSpacingMultiple: 1.3, margin: 0 });
  });
}

// ═══════════════ SLIDE 5 — POSITIONING ═══════════════
{
  const s = pptx.addSlide();
  addBg(s); addBar(s); addLabel(s, 'Positioning'); addFooter(s, 5);

  s.addText('Release Strategy', { x: 0.6, y: 0.6, w: 8, h: 0.5, fontSize: 34, fontFace: 'Arial Black', color: C.white, bold: true, margin: 0 });

  const tl = [
    { d: 'Q2 2027', l: 'Early Access', sub: 'Core gameplay, 4 courts,\nonline matchmaking', a: false },
    { d: 'Q4 2027', l: 'Full Launch', sub: '8 courts, story mode,\nranked play, 20+ characters', a: true },
    { d: '2028+', l: 'Live Service', sub: 'Seasonal content drops,\nnew courts & tournaments', a: false },
  ];
  tl.forEach((t, i) => {
    const x = 0.6 + i * 3.05;
    if (i < 2) s.addShape(pptx.ShapeType.rect, { x: x + 2.75, y: 2.15, w: 0.3, h: 0.03, fill: { color: C.gray } });
    s.addShape(pptx.ShapeType.rect, { x, y: 1.4, w: 2.75, h: 2.2, fill: { color: t.a ? C.blue : C.card }, rectRadius: 0.08 });
    s.addText(t.d, { x: x + 0.25, y: 1.55, w: 2.2, h: 0.25, fontSize: 10, fontFace: 'Calibri', color: t.a ? C.bg : C.gold, bold: true, letterSpacing: 1, margin: 0 });
    s.addText(t.l, { x: x + 0.25, y: 1.85, w: 2.2, h: 0.4, fontSize: 20, fontFace: 'Arial Black', color: t.a ? C.bg : C.white, bold: true, margin: 0 });
    s.addText(t.sub, { x: x + 0.25, y: 2.4, w: 2.2, h: 0.9, fontSize: 11, fontFace: 'Calibri', color: t.a ? '0A0E27' : C.gray, lineSpacingMultiple: 1.3, margin: 0 });
  });

  // Price
  s.addShape(pptx.ShapeType.rect, { x: 0.6, y: 3.95, w: 4.3, h: 1.0, fill: { color: C.card }, rectRadius: 0.08 });
  s.addText('$19.99', { x: 0.9, y: 4.0, w: 2.3, h: 0.9, fontSize: 30, fontFace: 'Arial Black', color: C.gold, bold: true, valign: 'middle', margin: 0 });
  s.addText('Premium Indie Tier\nDigital-first on PlayStation Store', { x: 3.0, y: 4.05, w: 1.8, h: 0.8, fontSize: 11, fontFace: 'Calibri', color: C.gray, lineSpacingMultiple: 1.3 });

  // Post-launch
  s.addShape(pptx.ShapeType.rect, { x: 5.1, y: 3.95, w: 4.3, h: 1.0, fill: { color: C.card }, rectRadius: 0.08 });
  s.addText('Post-Launch Content', { x: 5.4, y: 4.05, w: 3.7, h: 0.3, fontSize: 13, fontFace: 'Calibri', color: C.white, bold: true, margin: 0 });
  s.addText('Seasonal drops \u2014 new courts, characters,\nlimited-time tournament modes', { x: 5.4, y: 4.4, w: 3.7, h: 0.6, fontSize: 11, fontFace: 'Calibri', color: C.gray, lineSpacingMultiple: 1.3 });
}

// ═══════════════ SLIDE 6 — AUDIENCE ═══════════════
{
  const s = pptx.addSlide();
  addBg(s); addBar(s); addLabel(s, 'Audience'); addFooter(s, 6);

  s.addText('Who Plays', { x: 0.6, y: 0.6, w: 8, h: 0.5, fontSize: 34, fontFace: 'Arial Black', color: C.white, bold: true, margin: 0 });

  const aud = [
    { tag: 'PRIMARY', pct: '60%', t: 'Competitive Casuals', demo: 'Males 16\u201334', d: 'FIFA players who want something faster, more accessible, and more expressive.' },
    { tag: 'SECONDARY', pct: '25%', t: 'Couch Co-op Players', demo: 'Friends & families', d: 'Local 3v3 split-screen brings back the shared-screen sports game experience.' },
    { tag: 'TERTIARY', pct: '15%', t: 'Content Creators', demo: 'Streamers & clip makers', d: 'The trick system generates shareable highlights. Built-in replay tools.' },
  ];
  aud.forEach((a, i) => {
    const x = 0.6 + i * 3.05;
    s.addShape(pptx.ShapeType.rect, { x, y: 1.35, w: 2.75, h: 2.65, fill: { color: C.card }, rectRadius: 0.08 });
    s.addText(a.pct, { x: x + 0.2, y: 1.4, w: 0.9, h: 0.5, fontSize: 24, fontFace: 'Arial Black', color: C.blue, bold: true, margin: 0 });
    s.addText(a.tag, { x: x + 1.1, y: 1.5, w: 1.4, h: 0.2, fontSize: 8, fontFace: 'Calibri', color: C.gold, bold: true, letterSpacing: 2, margin: 0 });
    s.addText(a.t, { x: x + 0.2, y: 2.0, w: 2.3, h: 0.3, fontSize: 14, fontFace: 'Calibri', color: C.white, bold: true, margin: 0 });
    s.addText(a.demo, { x: x + 0.2, y: 2.3, w: 2.3, h: 0.2, fontSize: 10, fontFace: 'Calibri', color: C.blue, margin: 0 });
    s.addText(a.d, { x: x + 0.2, y: 2.65, w: 2.3, h: 1.1, fontSize: 10, fontFace: 'Calibri', color: C.gray, lineSpacingMultiple: 1.35, margin: 0 });
  });

  // Market gap
  s.addShape(pptx.ShapeType.rect, { x: 0.6, y: 4.25, w: 8.8, h: 0.75, fill: { color: C.darkBlue }, rectRadius: 0.08 });
  s.addText('14-YEAR MARKET GAP', { x: 0.9, y: 4.3, w: 3, h: 0.25, fontSize: 12, fontFace: 'Arial Black', color: C.gold, bold: true, margin: 0 });
  s.addText('No active street football franchise on PlayStation since FIFA Street 4 (2012). Massive unserved demand.', { x: 0.9, y: 4.6, w: 8.2, h: 0.3, fontSize: 11, fontFace: 'Calibri', color: C.body, margin: 0 });
}

// ═══════════════ SLIDE 7 — SCOPE ═══════════════
{
  const s = pptx.addSlide();
  addBg(s); addBar(s); addLabel(s, 'Scope'); addFooter(s, 7);

  s.addText('Features & Mechanics', { x: 0.6, y: 0.6, w: 8, h: 0.5, fontSize: 34, fontFace: 'Arial Black', color: C.white, bold: true, margin: 0 });

  const feats = [
    { t: '3v3 Online Multiplayer', d: 'Ranked and casual matchmaking' },
    { t: 'Local Co-op', d: 'Split-screen for up to 6 players' },
    { t: 'Story Mode', d: 'Campaign through global street leagues' },
    { t: 'Crew System', d: 'Recruit, customize, level up your squad' },
    { t: 'Trick Engine', d: '50+ moves with skill-based combos' },
    { t: 'Court Editor', d: 'Community courts, PS5 share integration' },
  ];
  feats.forEach((f, i) => {
    const col = i % 3, row = Math.floor(i / 3);
    const x = 0.6 + col * 3.05, y = 1.35 + row * 1.3;
    s.addShape(pptx.ShapeType.rect, { x, y, w: 2.75, h: 1.1, fill: { color: C.card }, rectRadius: 0.06 });
    s.addShape(pptx.ShapeType.ellipse, { x: x + 0.15, y: y + 0.15, w: 0.18, h: 0.18, fill: { color: C.blue } });
    s.addText(f.t, { x: x + 0.45, y: y + 0.1, w: 2.1, h: 0.25, fontSize: 12, fontFace: 'Calibri', color: C.white, bold: true, margin: 0 });
    s.addText(f.d, { x: x + 0.15, y: y + 0.45, w: 2.45, h: 0.5, fontSize: 10, fontFace: 'Calibri', color: C.gray, lineSpacingMultiple: 1.25, margin: 0 });
  });

  // DualSense bar
  s.addShape(pptx.ShapeType.rect, { x: 0.6, y: 4.1, w: 8.8, h: 0.7, fill: { color: C.blue }, rectRadius: 0.06 });
  s.addText('DUALSENSE INTEGRATION', { x: 0.9, y: 4.15, w: 3, h: 0.25, fontSize: 10, fontFace: 'Calibri', color: C.bg, bold: true, letterSpacing: 1, margin: 0 });
  s.addText('Haptic ball control  \u00B7  Adaptive trigger power shots  \u00B7  Controller speaker crowd chants', { x: 0.9, y: 4.42, w: 8, h: 0.25, fontSize: 11, fontFace: 'Calibri', color: '0A0E27', margin: 0 });

  s.addText('Team of 3\u20135  \u00B7  Unreal Engine 5  \u00B7  18-month production timeline', { x: 0.6, y: 4.85, w: 6, h: 0.25, fontSize: 9, fontFace: 'Calibri', color: C.gray });
}

// ═══════════════ SLIDE 8 — THEME (with court environment image) ═══════════════
{
  const s = pptx.addSlide();
  addBg(s); addBar(s); addLabel(s, 'Theme'); addFooter(s, 8);

  s.addText('Look & Feel', { x: 0.6, y: 0.6, w: 8, h: 0.5, fontSize: 34, fontFace: 'Arial Black', color: C.white, bold: true, margin: 0 });

  // Left — Art style
  s.addText('ART STYLE', { x: 0.6, y: 1.3, w: 2, h: 0.2, fontSize: 9, fontFace: 'Calibri', color: C.gold, bold: true, letterSpacing: 2, margin: 0 });
  s.addText('Stylized Semi-Realistic', { x: 0.6, y: 1.55, w: 4.2, h: 0.35, fontSize: 18, fontFace: 'Arial Black', color: C.white, bold: true, margin: 0 });
  s.addText(
    'Where Fortnite\'s expressiveness meets authentic street culture. Bold outlines, vibrant lighting, graffiti environments. Diverse, customizable characters with real streetwear.',
    { x: 0.6, y: 2.0, w: 4.2, h: 0.8, fontSize: 11, fontFace: 'Calibri', color: C.body, lineSpacingMultiple: 1.4 }
  );

  // Right — Court environment concept art (replaces color blocks)
  s.addImage({ path: courtImg, x: 5.1, y: 1.3, w: 4.35, h: 2.45, rounding: true });
  s.addText('Court Environment Concept', { x: 5.1, y: 3.55, w: 4.35, h: 0.2, fontSize: 8, fontFace: 'Calibri', color: C.gray, align: 'center' });

  // Audio section
  s.addShape(pptx.ShapeType.rect, { x: 0.6, y: 3.05, w: 4.2, h: 0.85, fill: { color: C.card }, rectRadius: 0.08 });
  s.addText('AUDIO', { x: 0.9, y: 3.12, w: 2, h: 0.2, fontSize: 9, fontFace: 'Calibri', color: C.gold, bold: true, letterSpacing: 2, margin: 0 });
  s.addText('Lo-fi hip-hop, electronic beats. Dynamic crowd reactions. Street ambience \u2014 traffic, boomboxes, urban life.', {
    x: 0.9, y: 3.35, w: 3.6, h: 0.45, fontSize: 10, fontFace: 'Calibri', color: C.gray, lineSpacingMultiple: 1.3,
  });

  // Inspiration refs
  s.addText('INSPIRATION', { x: 0.6, y: 4.15, w: 2, h: 0.2, fontSize: 9, fontFace: 'Calibri', color: C.gold, bold: true, letterSpacing: 2, margin: 0 });
  const refs = [
    { name: 'Jet Set Radio', what: 'Style' },
    { name: 'NBA Street', what: 'Gameplay' },
    { name: 'Rocket League', what: 'Comp. Loop' },
  ];
  refs.forEach((r, i) => {
    const x = 0.6 + i * 3.05;
    s.addShape(pptx.ShapeType.rect, { x, y: 4.4, w: 2.75, h: 0.45, fill: { color: C.card }, rectRadius: 0.05 });
    s.addText(`${r.name}  \u2014  ${r.what}`, { x, y: 4.4, w: 2.75, h: 0.45, fontSize: 10, fontFace: 'Calibri', color: C.body, align: 'center', valign: 'middle' });
  });
}

// ═══════════════ SLIDE 9 — SUPPORTING VISUALS (NEW) ═══════════════
{
  const s = pptx.addSlide();
  addBg(s); addBar(s); addLabel(s, 'Supporting Visuals'); addFooter(s, 9);

  s.addText('Concept Art', { x: 0.6, y: 0.6, w: 8, h: 0.5, fontSize: 34, fontFace: 'Arial Black', color: C.white, bold: true, margin: 0 });

  // Gameplay screenshot — large, left
  s.addImage({ path: gameplayImg, x: 0.6, y: 1.35, w: 5.5, h: 3.1, rounding: true });
  s.addText('In-Game Gameplay Concept', { x: 0.6, y: 4.3, w: 5.5, h: 0.2, fontSize: 8, fontFace: 'Calibri', color: C.gray, align: 'center' });

  // Character lineup — right side, stacked
  s.addImage({ path: charImg, x: 6.3, y: 1.35, w: 3.15, h: 1.77, rounding: true });
  s.addText('Character Roster Concept', { x: 6.3, y: 3.0, w: 3.15, h: 0.2, fontSize: 8, fontFace: 'Calibri', color: C.gray, align: 'center' });

  // Court environment — right side, below characters
  s.addImage({ path: courtImg, x: 6.3, y: 3.3, w: 3.15, h: 1.77, rounding: true });
  s.addText('Environment Concept', { x: 6.3, y: 4.95, w: 3.15, h: 0.2, fontSize: 8, fontFace: 'Calibri', color: C.gray, align: 'center' });
}

// ═══════════════ SLIDE 10 — TEAM & STUDIO ═══════════════
{
  const s = pptx.addSlide();
  addBg(s); addBar(s); addLabel(s, 'Team & Studio'); addFooter(s, 10);

  s.addText('About EasyChamp', { x: 0.6, y: 0.6, w: 8, h: 0.5, fontSize: 34, fontFace: 'Arial Black', color: C.white, bold: true, margin: 0 });

  // Company card with logo
  s.addShape(pptx.ShapeType.rect, { x: 0.6, y: 1.35, w: 4.3, h: 2.3, fill: { color: C.card }, rectRadius: 0.08 });
  s.addImage({ path: logoIcon, x: 0.9, y: 1.45, w: 0.22, h: 0.25 });
  s.addText('EASYCHAMP, INC.', { x: 1.2, y: 1.45, w: 3.5, h: 0.25, fontSize: 10, fontFace: 'Calibri', color: C.gold, bold: true, letterSpacing: 2, margin: 0 });

  const info = [
    ['Entity', 'Delaware C-Corporation'],
    ['Founded', 'August 2021'],
    ['Focus', 'Software & Interactive Entertainment'],
    ['HQ', 'Sunny Isles Beach, FL'],
    ['Team', '3\u20135 (founder + contractors)'],
  ];
  info.forEach((r, i) => {
    const y = 1.85 + i * 0.35;
    s.addText(r[0], { x: 0.9, y, w: 1.0, h: 0.25, fontSize: 10, fontFace: 'Calibri', color: C.gray, margin: 0 });
    s.addText(r[1], { x: 1.9, y, w: 2.8, h: 0.25, fontSize: 10, fontFace: 'Calibri', color: C.body, bold: true, margin: 0 });
  });

  // Founder card
  s.addShape(pptx.ShapeType.rect, { x: 5.1, y: 1.35, w: 4.3, h: 2.3, fill: { color: C.card }, rectRadius: 0.08 });
  s.addText('FOUNDER & CEO', { x: 5.4, y: 1.45, w: 3.5, h: 0.25, fontSize: 10, fontFace: 'Calibri', color: C.gold, bold: true, letterSpacing: 2, margin: 0 });
  s.addText('Anton Abyzov', { x: 5.4, y: 1.8, w: 3.7, h: 0.35, fontSize: 20, fontFace: 'Arial Black', color: C.white, bold: true, margin: 0 });
  s.addText(
    'Software engineer with 10+ years of experience building scalable systems and real-time applications. ' +
    'Leading the studio\'s expansion into interactive entertainment with a focus on multiplayer game architecture.',
    { x: 5.4, y: 2.25, w: 3.7, h: 1.1, fontSize: 10, fontFace: 'Calibri', color: C.gray, lineSpacingMultiple: 1.35 }
  );

  // Seeking bar
  s.addShape(pptx.ShapeType.rect, { x: 0.6, y: 3.9, w: 8.8, h: 0.65, fill: { color: C.blue }, rectRadius: 0.06 });
  s.addText('WHAT WE\u2019RE SEEKING', { x: 0.9, y: 3.95, w: 3, h: 0.2, fontSize: 9, fontFace: 'Calibri', color: C.bg, bold: true, letterSpacing: 2, margin: 0 });
  s.addText('PlayStation dev kit access to optimize for PS5 hardware, DualSense features, and console certification pipeline.', { x: 0.9, y: 4.2, w: 8.2, h: 0.25, fontSize: 11, fontFace: 'Calibri', color: '0A0E27', margin: 0 });

  // Status bar
  s.addShape(pptx.ShapeType.rect, { x: 0.6, y: 4.65, w: 8.8, h: 0.4, fill: { color: C.card }, rectRadius: 0.05 });
  s.addText('STATUS:  Core prototype in development  \u00B7  Unreal Engine 5  \u00B7  Vertical slice targeting Q3 2026', { x: 0.9, y: 4.65, w: 8.2, h: 0.4, fontSize: 10, fontFace: 'Calibri', color: C.body, valign: 'middle' });
}

// ═══════════════ SLIDE 11 — CONTACT ═══════════════
{
  const s = pptx.addSlide();
  addBg(s);

  // Decorative
  s.addShape(pptx.ShapeType.ellipse, { x: -2.0, y: 2.8, w: 4.5, h: 4.5, fill: { color: C.darkBlue } });

  // EasyChamp logo with label (centered, top area)
  s.addImage({ path: logoLabel, x: 0.6, y: 0.5, w: 2.4, h: 0.4 });

  s.addText('Thank you.', {
    x: 0.6, y: 1.1, w: 8.5, h: 0.7,
    fontSize: 44, fontFace: 'Arial Black', color: C.white, bold: true, margin: 0,
  });
  s.addText("Let\u2019s build something great for PlayStation.", {
    x: 0.6, y: 1.85, w: 7, h: 0.3,
    fontSize: 15, fontFace: 'Calibri', color: C.blue,
  });

  // Contact card
  s.addShape(pptx.ShapeType.rect, { x: 0.6, y: 2.4, w: 5.5, h: 2.1, fill: { color: C.card }, rectRadius: 0.08 });
  const contact = [
    ['Company', 'EasyChamp, Inc.'],
    ['Contact', 'Anton Abyzov \u2014 Founder & CEO'],
    ['Email', 'admin@easychamp.com'],
    ['Location', 'Sunny Isles Beach, FL, USA'],
    ['Web', 'easychamp.com'],
  ];
  contact.forEach((c, i) => {
    const y = 2.55 + i * 0.36;
    s.addText(c[0], { x: 0.9, y, w: 1.2, h: 0.28, fontSize: 11, fontFace: 'Calibri', color: C.gray, margin: 0 });
    s.addText(c[1], { x: 2.1, y, w: 3.8, h: 0.28, fontSize: 11, fontFace: 'Calibri', color: C.body, bold: true, margin: 0 });
  });

  // Decorative (right)
  s.addShape(pptx.ShapeType.ellipse, { x: 8.0, y: 3.2, w: 0.5, h: 0.5, fill: { color: C.blue } });
  s.addShape(pptx.ShapeType.ellipse, { x: 8.7, y: 2.9, w: 0.12, h: 0.12, fill: { color: C.gold } });

  // Bottom bar
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 4.75, w: SW, h: 0.6, fill: { color: C.darkBlue } });
  s.addText('EASYCHAMP, INC.', { x: 0.6, y: 4.8, w: 4, h: 0.45, fontSize: 12, fontFace: 'Calibri', color: C.gold, bold: true, letterSpacing: 4, valign: 'middle' });
  s.addText('CONFIDENTIAL', { x: 7.0, y: 4.8, w: 2.5, h: 0.45, fontSize: 9, fontFace: 'Calibri', color: C.gray, align: 'right', letterSpacing: 2, valign: 'middle' });
}

// ── Export ──
const outPath = '/Users/antonabyzov/Projects/github/specweave-umb/tools/street-champ-pitch.pptx';
await pptx.writeFile({ fileName: outPath });
console.log(`Saved: ${outPath}`);
