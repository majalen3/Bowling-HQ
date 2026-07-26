export type BoardStatus = 'backlog' | 'in_progress' | 'done';

export type ProgressItem = {
  id: string;
  title: string;
  status: BoardStatus;
  done_criteria: string[];
};

export type ProgressSnapshot = {
  finished_target: string;
  scope_lock: string[];
  release_gate: string[];
  board: ProgressItem[];
};
