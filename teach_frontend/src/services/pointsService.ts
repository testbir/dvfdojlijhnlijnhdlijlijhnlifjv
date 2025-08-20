// frontend/src/services/pointsService.ts
import { pointsApi } from "../api/axiosInstance";

export interface PointsBalance {
  balance: number;
  user_id: number;
}

export interface PointsTransaction {
  id: number;
  user_id: number;
  amount: number;
  operation_type: 'award' | 'spend' | 'refund';
  description: string;
  reference_type?: string;
  reference_id?: number;
  created_at: string;
}

class PointsService {
  async getBalance(): Promise<PointsBalance> {
    const response = await pointsApi.get("/v1/public/balance/");
    return response.data;
  }

  async getTransactions(params?: {
    limit?: number;
    offset?: number;
  }): Promise<{
    items: PointsTransaction[];
    total: number;
    limit: number;
    offset: number;
  }> {
    const response = await pointsApi.get("/v1/public/transactions/", { params });
    return response.data;
  }

  async getPointsStats(): Promise<{
    total_earned: number;
    total_spent: number;
    current_balance: number;
  }> {
    const response = await pointsApi.get("/v1/public/stats/");
    return response.data;
  }
}

export default new PointsService();
