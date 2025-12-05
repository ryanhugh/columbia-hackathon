import axios, { AxiosInstance } from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '30000'),
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface TradeSignal {
  market_id: string;
  strategy: string;
  confidence: number;
  direction: 'YES' | 'NO';
  reasoning: string;
  proof_link: string;
  timestamp?: string;
}

export interface AnalysisState {
  market_slug: string;
  current_odds: number;
  narrative_score: number;
  fundamental_truth: string;
  decision: string;
  reality_odds?: number;
  gap?: number;
}

export interface SignalResponse {
  state: AnalysisState;
  card: TradeSignal;
  upload: any;
  audio_file?: string;
  audio_url?: string;
}

export interface MarketData {
  id: string;
  slug: string;
  title: string;
  description: string;
  image_url?: string;
  current_odds?: number;
  volume_24h?: number;
  outcomes: {
    name: string;
    odds: number;
  }[];
}

class APIService {
  // Trade Analysis Endpoints
  async analyzeWithSPOON(marketSlug: string): Promise<SignalResponse> {
    const response = await apiClient.post('/spoon/trade', {
      market_slug: marketSlug,
    });
    return response.data;
  }

  async analyzeWithPolycaster(
    marketSlug: string,
    query?: string,
    category?: string,
    useManus?: boolean
  ): Promise<SignalResponse> {
    const response = await apiClient.post('/polycaster/signal', {
      market_slug: marketSlug,
      query,
      category: category || 'crypto',
      use_manus: useManus || false,
    });
    return response.data;
  }

  // Market Data Endpoints
  async getMarkets(params?: any): Promise<MarketData[]> {
    const response = await apiClient.get('/polymarket/list', { params });
    return response.data;
  }

  async getMarketDetails(marketSlug: string): Promise<MarketData> {
    const response = await apiClient.get(`/polymarket/${marketSlug}`);
    return response.data;
  }

  // Sentiment Analysis
  async analyzeSentiment(marketSlug: string): Promise<any> {
    const response = await apiClient.get('/polycaster/sentiment', {
      params: { market_slug: marketSlug },
    });
    return response.data;
  }

  // Manipulation Detection
  async inspectManipulation(marketData: any): Promise<any> {
    const response = await apiClient.post('/polycop/inspect', marketData);
    return response.data;
  }

  // Podcast/Audio Generation
  async generatePodcast(marketSlug: string, analysis: AnalysisState): Promise<string> {
    const response = await apiClient.post('/polycaster/podcast', {
      market_slug: marketSlug,
      analysis,
    });
    return response.data.audio_url;
  }

  // AI Chat Completions
  async chatWithAI(query: string, context?: any): Promise<string> {
    const response = await apiClient.post('/sudo/chat', {
      query,
      context,
    });
    return response.data.response;
  }

  // Whale Activity
  async getWhaleActivity(limit?: number): Promise<any[]> {
    const response = await apiClient.get('/polywhaler/feeds', {
      params: { limit: limit || 20 },
    });
    return response.data;
  }

  // Error handler
  getErrorMessage(error: any): string {
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }
    if (error.message) {
      return error.message;
    }
    return 'An error occurred. Please try again.';
  }
}

export default new APIService();
