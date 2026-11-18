/*
 * ============================================================
 *  Tank Battle - M5Stack Cardputer-ADV
 *  Display: ST7789 240x135, rotation 0 = landscape
 *
 *  ===== 2 PLAYER MODE: NO AI, P1 vs P2 only =====
 *
 *  Player 1 (GREEN)              Player 2 (BLUE)
 *    W A S D  move                 ARROW KEYS  move
 *    X    fire                     ENTER   fire
 *
 *  Arrow key positions on ADV (verified):
 *    UP    = (11, 2)
 *    LEFT  = (10, 3)
 *    DOWN  = (11, 3)
 *    RIGHT = (12, 3)
 *
 *  TAB  pause     ESC  restart
 * ============================================================
 */

#include "M5Cardputer.h"

constexpr int SCREEN_W = 240;
constexpr int SCREEN_H = 135;

constexpr int WALL = 8;
constexpr int COLS = 30;
constexpr int ROWS = 17;

const uint8_t MAP_INIT[ROWS][COLS] = {
  {2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2},
  {2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2},
  {2,0,1,1,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,2},
  {2,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,2},
  {2,0,0,0,0,0,2,2,0,0,0,0,0,0,0,0,0,0,2,2,0,0,0,0,0,0,0,0,0,2},
  {2,0,0,0,0,0,2,2,0,0,1,1,1,1,1,1,0,0,2,2,0,0,0,0,1,1,0,0,0,2},
  {2,0,1,1,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,1,1,1,1,0,0,0,2},
  {2,0,1,1,0,0,0,0,0,0,1,0,3,3,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,2},
  {2,0,0,0,0,0,0,0,0,0,1,0,3,3,0,1,0,0,0,0,2,2,0,0,0,0,0,0,0,2},
  {2,0,1,1,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,2,2,0,0,1,1,1,1,0,2},
  {2,0,1,1,0,0,2,2,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,0,2},
  {2,0,0,0,0,0,2,2,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,2},
  {2,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,1,1,0,0,1,1,1,1,0,2},
  {2,0,1,1,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,2},
  {2,0,1,1,0,0,0,0,0,0,1,0,3,3,0,0,1,0,0,0,0,0,1,1,0,0,0,0,0,2},
  {2,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,1,1,0,0,0,0,0,2},
  {2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2},
};

uint8_t gmap[ROWS][COLS];

struct Bullet { float x, y, vx, vy; bool alive; int owner; };
struct Tank   { float x, y; int w, h, dir; bool alive; int cooldown; int hp; };
struct Enemy  { float x, y; int dir, moveTimer, shootTimer; bool alive; };

Tank   p1, p2;
Enemy  enemies[8];
Bullet bullets[24];

int    enemyCount = 0, spawnTimer = 0;
int    killsP1 = 0, killsP2 = 0;
int    livesP1 = 3, livesP2 = 3;
bool   twoPlayer = true;
bool   paused = false, gameOver = false, win = false;

bool   prevFireP1 = false, prevFireP2 = false, prevTab = false, prevEnter = false;

M5Canvas canvas(&M5.Display);

// ============================================================
//  helpers
// ============================================================
bool tankBlocked(float nx, float ny, int w, int h) {
  if (nx < 0 || ny < 0 || nx + w > SCREEN_W || ny + h > SCREEN_H) return true;
  int c0 = (int)nx / WALL, c1 = (int)(nx + w - 1) / WALL;
  int r0 = (int)ny / WALL, r1 = (int)(ny + h - 1) / WALL;
  for (int r = r0; r <= r1; r++)
    for (int c = c0; c <= c1; c++) {
      if (r < 0 || r >= ROWS || c < 0 || c >= COLS) return true;
      if (gmap[r][c] != 0 && gmap[r][c] != 3) return true;
    }
  return false;
}

uint8_t cellAt(float x, float y) {
  int c = (int)x / WALL, r = (int)y / WALL;
  if (r < 0 || r >= ROWS || c < 0 || c >= COLS) return 2;
  return gmap[r][c];
}

void breakCell(float x, float y) {
  int c = (int)x / WALL, r = (int)y / WALL;
  if (r >= 0 && r < ROWS && c >= 0 && c < COLS && gmap[r][c] == 1) gmap[r][c] = 0;
}

// ============================================================
//  按键
// ============================================================
bool wordHas(char lo) {
  auto &ks = M5Cardputer.Keyboard.keysState();
  for (char c : ks.word) {
    if (c == lo || c == (char)(lo - 32)) return true;
  }
  return false;
}

// 坐标判断按键
bool keyAt(int tx, int ty) {
  for (auto &p : M5Cardputer.Keyboard.keyList()) {
    if (p.x == tx && p.y == ty) return true;
  }
  return false;
}

// 精确方向键判定 (ADV 实测坐标)
bool arrowLeft()  { return keyAt(10, 3); }
bool arrowDown()  { return keyAt(11, 3); }
bool arrowRight() { return keyAt(12, 3); }
bool arrowUp()    { return keyAt(11, 2); }

// ============================================================
void resetGame() {
  memcpy(gmap, MAP_INIT, sizeof(gmap));

  p1.w = 12; p1.h = 12;
  p1.x = 4 * WALL; p1.y = 13 * WALL;
  p1.dir = 0; p1.alive = true; p1.cooldown = 0; p1.hp = 3;

  p2.w = 12; p2.h = 12;
  p2.x = 25 * WALL; p2.y = 13 * WALL;
  p2.dir = 0; p2.alive = true; p2.cooldown = 0; p2.hp = 3;

  for (int i = 0; i < 24; i++) bullets[i].alive = false;
  for (int i = 0; i < 8; i++)  enemies[i].alive = false;

  enemyCount = 0; spawnTimer = 0;
  killsP1 = 0; killsP2 = 0;
  livesP1 = 3; livesP2 = 3;
  paused = false; gameOver = false; win = false;

  prevFireP1 = prevFireP2 = prevTab = prevEnter = false;
}

void spawnEnemy() {
  for (int i = 0; i < 8; i++) {
    if (enemies[i].alive) continue;
    for (int t = 0; t < 25; t++) {
      int col = random(1, COLS - 1);
      float ex = col * WALL, ey = WALL;
      if (!tankBlocked(ex, ey, 12, 12)) {
        enemies[i].alive = true;
        enemies[i].x = ex; enemies[i].y = ey;
        enemies[i].dir = 2;
        enemies[i].moveTimer  = random(20, 60);
        enemies[i].shootTimer = random(30, 90);
        enemyCount++;
        return;
      }
    }
  }
}

void fireAt(float x, float y, int dir, int owner) {
  for (int i = 0; i < 24; i++) {
    if (bullets[i].alive) continue;
    bullets[i].x = x; bullets[i].y = y;
    bullets[i].vx = 0; bullets[i].vy = 0;
    bullets[i].alive = true; bullets[i].owner = owner;
    switch (dir) {
      case 0: bullets[i].vy = -2.5f; break;
      case 1: bullets[i].vx =  2.5f; break;
      case 2: bullets[i].vy =  2.5f; break;
      default: bullets[i].vx = -2.5f; break;
    }
    return;
  }
}

void fireTank(Tank &t, int owner) {
  float bx = t.x + 5, by = t.y + 5;
  switch (t.dir) {
    case 0: by = t.y - 3; break;
    case 1: bx = t.x + 13; break;
    case 2: by = t.y + 13; break;
    default: bx = t.x - 3; break;
  }
  fireAt(bx, by, t.dir, owner);
}

void moveTank(Tank &t, bool up, bool down, bool left, bool right) {
  float nx = t.x, ny = t.y;
  const float sp = 1.6f;
  if (up)         { t.dir = 0; ny -= sp; }
  else if (down)  { t.dir = 2; ny += sp; }
  else if (left)  { t.dir = 3; nx -= sp; }
  else if (right) { t.dir = 1; nx += sp; }
  if (!tankBlocked(nx, ny, t.w, t.h)) { t.x = nx; t.y = ny; }
}

// ============================================================
void updatePlayers() {
  if (p1.cooldown > 0) p1.cooldown--;
  if (p2.cooldown > 0) p2.cooldown--;

  auto &ks = M5Cardputer.Keyboard.keysState();

  // ---- P1: W A S D + X ----
  if (p1.alive) {
    moveTank(p1, wordHas('w'), wordHas('s'), wordHas('a'), wordHas('d'));
    bool fire = wordHas('x');
    if (fire && !prevFireP1 && p1.cooldown <= 0) {
      fireTank(p1, 1);
      p1.cooldown = 12;
    }
    prevFireP1 = fire;
  } else prevFireP1 = wordHas('x');

  // ---- P2: ARROWS + ENTER ----
  if (twoPlayer && p2.alive) {
    moveTank(p2, arrowUp(), arrowDown(), arrowLeft(), arrowRight());
    bool fire = ks.enter;
    if (fire && !prevFireP2 && p2.cooldown <= 0) {
      fireTank(p2, 2);
      p2.cooldown = 12;
    }
    prevFireP2 = fire;
  } else prevFireP2 = ks.enter;
}

void updateEnemies() {
  for (int i = 0; i < 8; i++) {
    if (!enemies[i].alive) continue;
    Enemy &e = enemies[i];

    if (--e.moveTimer <= 0) {
      e.dir = random(0, 4);
      e.moveTimer = random(30, 80);
    }

    float nx = e.x, ny = e.y;
    const float sp = 0.7f;
    switch (e.dir) {
      case 0: ny -= sp; break;
      case 1: nx += sp; break;
      case 2: ny += sp; break;
      default: nx -= sp; break;
    }
    if (!tankBlocked(nx, ny, 12, 12)) { e.x = nx; e.y = ny; }
    else e.moveTimer = 0;

    if (--e.shootTimer <= 0) {
      e.shootTimer = random(40, 100);
      float tx = p1.x, ty = p1.y;
      if (!p1.alive) { tx = p2.x; ty = p2.y; }
      int d = e.dir;
      float dx = tx - e.x, dy = ty - e.y;
      if (fabs(dx) > fabs(dy)) d = (dx > 0) ? 1 : 3;
      else                     d = (dy > 0) ? 2 : 0;

      float bx = e.x + 5, by = e.y + 5;
      switch (d) {
        case 0: by = e.y - 3; break;
        case 1: bx = e.x + 13; break;
        case 2: by = e.y + 13; break;
        default: bx = e.x - 3; break;
      }
      fireAt(bx, by, d, 0);
    }

    if (p1.alive && fabs(e.x - p1.x) < 11 && fabs(e.y - p1.y) < 11) {
      if (--livesP1 <= 0) p1.alive = false;
    }
  }
}

void updateBullets() {
  for (int i = 0; i < 24; i++) {
    if (!bullets[i].alive) continue;
    Bullet &b = bullets[i];
    b.x += b.vx; b.y += b.vy;

    if (b.x < 0 || b.x > SCREEN_W || b.y < 0 || b.y > SCREEN_H) { b.alive = false; continue; }

    uint8_t cell = cellAt(b.x, b.y);
    if (cell == 1) { breakCell(b.x, b.y); b.alive = false; continue; }
    if (cell == 2 || cell == 3) { b.alive = false; continue; }

    // --- 双人模式: P1/P2 互相打 ---
    if (twoPlayer) {
      if (b.owner == 1 && p2.alive &&
          b.x > p2.x && b.x < p2.x + 12 && b.y > p2.y && b.y < p2.y + 12) {
        b.alive = false;
        if (--p2.hp <= 0) {
          p2.alive = false;
          if (killsP1 >= 2) { win = true; gameOver = true; }
        } else {
          p2.x = 25 * WALL; p2.y = 13 * WALL;
        }
        killsP1++;
        continue;
      }
      if (b.owner == 2 && p1.alive &&
          b.x > p1.x && b.x < p1.x + 12 && b.y > p1.y && b.y < p1.y + 12) {
        b.alive = false;
        if (--p1.hp <= 0) {
          p1.alive = false;
          if (killsP2 >= 2) { win = true; gameOver = true; }
        } else {
          p1.x = 4 * WALL; p1.y = 13 * WALL;
        }
        killsP2++;
        continue;
      }
      // 敌人子弹(单人不刷, 保险起见)
      if (b.owner == 0) {
        if (p1.alive &&
            b.x > p1.x && b.x < p1.x + 12 && b.y > p1.y && b.y < p1.y + 12) {
          b.alive = false;
          if (--livesP1 <= 0) p1.alive = false;
        }
        if (p2.alive &&
            b.x > p2.x && b.x < p2.x + 12 && b.y > p2.y && b.y < p2.y + 12) {
          b.alive = false;
          if (--livesP2 <= 0) p2.alive = false;
        }
      }
    }
    // --- 单人模式: 打 AI ---
    else {
      if (b.owner == 1) {
        for (int j = 0; j < 8; j++) {
          if (!enemies[j].alive) continue;
          if (b.x > enemies[j].x && b.x < enemies[j].x + 12 &&
              b.y > enemies[j].y && b.y < enemies[j].y + 12) {
            enemies[j].alive = false; b.alive = false;
            enemyCount--; killsP1++;
            if (killsP1 >= 20) { win = true; gameOver = true; }
            break;
          }
        }
      } else if (p1.alive) {
        if (b.x > p1.x && b.x < p1.x + 12 && b.y > p1.y && b.y < p1.y + 12) {
          b.alive = false;
          if (--livesP1 <= 0) p1.alive = false;
          else { p1.x = 4 * WALL; p1.y = 13 * WALL; }
        }
      }
    }
  }
}

// ============================================================
//  渲染
// ============================================================
void drawMap() {
  for (int r = 0; r < ROWS; r++) {
    for (int c = 0; c < COLS; c++) {
      int x = c * WALL, y = r * WALL;
      switch (gmap[r][c]) {
        case 1:
          canvas.drawFastHLine(x, y, WALL, 0x8B45);
          canvas.drawFastHLine(x, y + 3, WALL, 0x8B45);
          canvas.drawFastHLine(x, y + 6, WALL, 0x8B45);
          break;
        case 2:
          canvas.fillRect(x, y, WALL, WALL, 0x7BEF);
          canvas.drawRect(x, y, WALL, WALL, 0xCE79);
          break;
        case 3:
          canvas.fillRect(x, y, WALL, WALL, 0x0410);
          canvas.drawFastHLine(x, y + 4, WALL, 0x04BF);
          break;
      }
    }
  }
}

void drawTank(float x, float y, int dir, uint16_t body, uint16_t body2) {
  canvas.fillRoundRect((int)x, (int)y, 12, 12, 2, body);
  canvas.fillRect((int)x + 3, (int)y + 3, 6, 6, body2);
  switch (dir) {
    case 0: canvas.fillRect((int)x + 5, (int)y - 3,  2, 4, TFT_WHITE); break;
    case 1: canvas.fillRect((int)x + 11, (int)y + 5, 4, 2, TFT_WHITE); break;
    case 2: canvas.fillRect((int)x + 5, (int)y + 11, 2, 4, TFT_WHITE); break;
    case 3: canvas.fillRect((int)x - 3, (int)y + 5,  4, 2, TFT_WHITE); break;
  }
}

void drawScoreboard() {
  int bx = SCREEN_W - 94, by = 0;
  canvas.fillRect(bx, by, 94, 12, 0x1082);
  canvas.drawRect(bx, by, 94, 12, 0x4208);

  canvas.setTextSize(1);

  // P1 击杀 + HP
  canvas.setTextColor(0x07E0, 0x1082);
  canvas.setCursor(bx + 2, by + 2);
  canvas.printf("P1 %d", killsP1);
  for (int i = 0; i < 3; i++)
    canvas.fillRect(bx + 24 + i * 5, by + 3, 3, 5,
                    (i < p1.hp) ? 0x07E0 : 0x2945);

  // P2 击杀 + HP
  canvas.setTextColor(0x07FF, 0x1082);
  canvas.setCursor(bx + 50, by + 2);
  canvas.printf("P2 %d", killsP2);
  for (int i = 0; i < 3; i++)
    canvas.fillRect(bx + 72 + i * 5, by + 3, 3, 5,
                    (i < p2.hp) ? 0x07FF : 0x2945);
}

void render() {
  canvas.fillScreen(TFT_BLACK);
  drawMap();

  if (!twoPlayer) {
    for (int i = 0; i < 8; i++)
      if (enemies[i].alive) drawTank(enemies[i].x, enemies[i].y, enemies[i].dir, 0xF800, 0x9000);
  }

  if (p1.alive) drawTank(p1.x, p1.y, p1.dir, 0x07E0, 0x05C0);
  if (twoPlayer && p2.alive) drawTank(p2.x, p2.y, p2.dir, 0x03EF, 0x0250);

  for (int i = 0; i < 24; i++) {
    if (!bullets[i].alive) continue;
    uint16_t col = (bullets[i].owner == 1) ? TFT_YELLOW
                 : (bullets[i].owner == 2) ? 0x07FF : 0xFD20;
    canvas.fillRect((int)bullets[i].x, (int)bullets[i].y, 2, 2, col);
  }

  drawScoreboard();

  if (paused || gameOver) {
    canvas.fillRect(52, 46, 136, 44, TFT_BLACK);
    canvas.drawRect(52, 46, 136, 44, TFT_WHITE);
    canvas.setTextSize(2);
    canvas.setTextColor(TFT_YELLOW, TFT_BLACK);
    canvas.setCursor(64, 52);
    if (win) {
      if (killsP1 > killsP2)      canvas.print("P1 WINS!");
      else if (killsP2 > killsP1) canvas.print("P2 WINS!");
      else                        canvas.print("WINNER!");
    } else if (gameOver) canvas.print("GAME OVER");
    else                 canvas.print("PAUSED");

    canvas.setTextSize(1);
    canvas.setTextColor(TFT_WHITE, TFT_BLACK);
    canvas.setCursor(66, 76);
    canvas.print("ESC = restart");
  }
}

void showTitle() {
  canvas.fillScreen(TFT_BLACK);
  canvas.setTextSize(2);
  canvas.setTextColor(TFT_GREEN, TFT_BLACK);
  canvas.setCursor(26, 6);
  canvas.print("TANK BATTLE");
  canvas.setTextSize(1);

  canvas.setTextColor(0x07E0, TFT_BLACK);
  canvas.setCursor(8, 32);
  canvas.print("P1: W A S D   FIRE: X");

  canvas.setTextColor(0x07FF, TFT_BLACK);
  canvas.setCursor(8, 44);
  canvas.print("P2: ARROWS    FIRE: ENTER");

  canvas.setTextColor(TFT_WHITE, TFT_BLACK);
  canvas.setCursor(8, 60);
  canvas.print("TAB pause");
  canvas.setCursor(8, 72);
  canvas.print("1 = 1P(bots)  2 = 2P(duel)");

  canvas.setCursor(8, 88);
  canvas.print("mode: ");
  canvas.setTextColor(TFT_YELLOW, TFT_BLACK);
  canvas.print(twoPlayer ? "2P DUEL" : "1P vs AI");

  canvas.setTextColor(TFT_WHITE, TFT_BLACK);
  canvas.setCursor(8, 110);
  canvas.print("X / ENTER to start");
  canvas.pushSprite(0, 0);
}

// ============================================================
void setup() {
  auto cfg = M5.config();
  M5Cardputer.begin(cfg, true);

  M5Cardputer.Display.setRotation(0);
  M5Cardputer.Display.fillScreen(TFT_BLACK);

  canvas.createSprite(SCREEN_W, SCREEN_H);
  canvas.setTextSize(1);

  randomSeed(esp_random());
  resetGame();

  bool start = false;
  while (!start) {
    M5Cardputer.update();
    auto &ks = M5Cardputer.Keyboard.keysState();

    if (wordHas('1')) twoPlayer = false;
    if (wordHas('2')) twoPlayer = true;
    if (wordHas('x') || ks.enter) start = true;

    showTitle();
    delay(60);
  }

  if (!twoPlayer) {
    for (int i = 0; i < 3; i++) spawnEnemy();
  }
  delay(200);
}

void loop() {
  M5Cardputer.update();
  auto &ks = M5Cardputer.Keyboard.keysState();

  if (ks.tab && !prevTab && !gameOver) paused = !paused;
  prevTab = ks.tab;

  static bool prevEsc = false;
  bool escDown = keyAt(0, 0);
  if (gameOver && escDown && !prevEsc) {
    resetGame();
    if (!twoPlayer) for (int i = 0; i < 3; i++) spawnEnemy();
  }
  prevEsc = escDown;

  updatePlayers();

  if (!paused && !gameOver) {
    if (!twoPlayer) {
      updateEnemies();
      if (++spawnTimer > 150) {
        spawnTimer = 0;
        if (enemyCount < 3) spawnEnemy();
      }
    }
    updateBullets();

    if (!p1.alive && (!twoPlayer || !p2.alive)) gameOver = true;
  }

  render();
  canvas.pushSprite(0, 0);
  delay(16);
}
