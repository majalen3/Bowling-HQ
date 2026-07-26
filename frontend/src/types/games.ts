export type GameItem = {
  id: string;
  session_id: string;
  game_number: number;
  score: number;
  created_at: string;
};

export type GamesResponse = {
  session_id: string;
  games: GameItem[];
  count: number;
  average: number;
};

export type ScoreImportResult = {
  session_id: string;
  games_imported: number;
  scores: number[];
  errors: string[];
};

export type ScoreImportRequest = {
  csv_text: string;
  source: string;
};

export type FrameItem = {
  id: string;
  game_id: string;
  frame_number: number;
  ball1: number;
  ball2: number | null;
  ball3: number | null;
  is_strike: boolean;
  is_spare: boolean;
};

export type FramesResponse = {
  game_id: string;
  frames: FrameItem[];
};
