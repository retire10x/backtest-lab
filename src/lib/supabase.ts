import { createClient, type SupabaseClient } from '@supabase/supabase-js';

const url = import.meta.env.PUBLIC_SUPABASE_URL;
const anonKey = import.meta.env.PUBLIC_SUPABASE_ANON_KEY;

// 환경변수가 아직 설정 안 된 상태(로컬 최초 빌드, 프리뷰 배포 전 등)에서도
// 빌드/렌더링이 죽지 않도록 null을 허용한다. 페이지 쪽에서 null 체크 후
// "데이터 준비 중" 문구를 보여준다.
export const supabase: SupabaseClient | null =
  url && anonKey ? createClient(url, anonKey) : null;

export type MonthlySignal = {
  id: number;
  strategy_slug: string;
  signal_date: string;
  kospi_return_12m: number;
  bond_return_12m: number;
  selected_asset: 'kospi' | 'bond' | 'cash';
  created_at: string;
};

export type BacktestSummary = {
  id: number;
  strategy_slug: string;
  period_start: string;
  period_end: string;
  cagr: number;
  mdd: number;
  total_return: number;
  savings_bank_rate: number;
  beats_savings_bank: boolean;
  passive_benchmark_cagr: number | null;
  passive_benchmark_mdd: number | null;
  verdict: string | null;
  verdict_note: string | null;
  updated_at: string;
};

export type WalkForwardResult = {
  id: number;
  strategy_slug: string;
  year: number;
  annual_return: number;
  mdd: number;
  beats_savings_bank: boolean;
  note: string | null;
};

const STRATEGY_SLUG = 'dual-momentum-kospi-bond';

export async function getLatestSignal(): Promise<MonthlySignal | null> {
  if (!supabase) return null;
  const { data, error } = await supabase
    .from('monthly_signals')
    .select('*')
    .eq('strategy_slug', STRATEGY_SLUG)
    .order('signal_date', { ascending: false })
    .limit(1)
    .maybeSingle();
  if (error) {
    console.error('getLatestSignal error:', error.message);
    return null;
  }
  return data;
}

export async function getSignalHistory(limit = 24): Promise<MonthlySignal[]> {
  if (!supabase) return [];
  const { data, error } = await supabase
    .from('monthly_signals')
    .select('*')
    .eq('strategy_slug', STRATEGY_SLUG)
    .order('signal_date', { ascending: false })
    .limit(limit);
  if (error) {
    console.error('getSignalHistory error:', error.message);
    return [];
  }
  return data ?? [];
}

export async function getLatestBacktestSummary(): Promise<BacktestSummary | null> {
  if (!supabase) return null;
  const { data, error } = await supabase
    .from('backtest_summaries')
    .select('*')
    .eq('strategy_slug', STRATEGY_SLUG)
    .order('updated_at', { ascending: false })
    .limit(1)
    .maybeSingle();
  if (error) {
    console.error('getLatestBacktestSummary error:', error.message);
    return null;
  }
  return data;
}

export async function getWalkForwardResults(): Promise<WalkForwardResult[]> {
  if (!supabase) return [];
  const { data, error } = await supabase
    .from('walk_forward_results')
    .select('*')
    .eq('strategy_slug', STRATEGY_SLUG)
    .order('year', { ascending: true });
  if (error) {
    console.error('getWalkForwardResults error:', error.message);
    return [];
  }
  return data ?? [];
}
