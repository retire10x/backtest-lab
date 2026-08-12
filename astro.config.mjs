import { defineConfig } from 'astro/config';
import vercel from '@astrojs/vercel';

// 서버 출력 모드: Supabase 데이터를 요청 시점에 읽어서 렌더링한다.
// (별도 프로그램이 DB를 갱신하면, 재배포 없이도 다음 요청부터 반영됨)
// 각 페이지에서 Cache-Control 헤더로 CDN 캐시를 걸어 정적 사이트에
// 가까운 속도/비용을 유지한다.
export default defineConfig({
  output: 'server',
  adapter: vercel({
    webAnalytics: { enabled: false },
  }),
  site: 'https://example.com', // TODO: 실제 도메인 연결 후 수정
});
