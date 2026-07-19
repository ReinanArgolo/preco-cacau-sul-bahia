export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "14.5"
  }
  public: {
    Tables: {
      data_quality_events: {
        Row: {
          check_name: string
          created_at: string
          details: Json
          id: number
          message: string
          observation_date: string | null
          severity: string
          source: string
        }
        Insert: {
          check_name: string
          created_at?: string
          details?: Json
          id?: never
          message: string
          observation_date?: string | null
          severity: string
          source: string
        }
        Update: {
          check_name?: string
          created_at?: string
          details?: Json
          id?: never
          message?: string
          observation_date?: string | null
          severity?: string
          source?: string
        }
        Relationships: []
      }
      exchange_rates_daily: {
        Row: {
          bulletin_type: string | null
          buy_rate: number
          content_checksum: string
          currency_pair: string
          first_collected_at: string
          last_collected_at: string
          metadata: Json
          observation_date: string
          previous_checksum: string | null
          quoted_at: string | null
          sell_rate: number
          source: string
          source_url: string
        }
        Insert: {
          bulletin_type?: string | null
          buy_rate: number
          content_checksum: string
          currency_pair: string
          first_collected_at?: string
          last_collected_at?: string
          metadata?: Json
          observation_date: string
          previous_checksum?: string | null
          quoted_at?: string | null
          sell_rate: number
          source: string
          source_url: string
        }
        Update: {
          bulletin_type?: string | null
          buy_rate?: number
          content_checksum?: string
          currency_pair?: string
          first_collected_at?: string
          last_collected_at?: string
          metadata?: Json
          observation_date?: string
          previous_checksum?: string | null
          quoted_at?: string | null
          sell_rate?: number
          source?: string
          source_url?: string
        }
        Relationships: []
      }
      ingestion_runs: {
        Row: {
          checksum: string | null
          coverage_end: string | null
          coverage_start: string | null
          error: string | null
          finished_at: string | null
          id: string
          requested_end: string
          requested_start: string
          row_count: number
          source: string
          started_at: string
          status: string
          warnings: Json
        }
        Insert: {
          checksum?: string | null
          coverage_end?: string | null
          coverage_start?: string | null
          error?: string | null
          finished_at?: string | null
          id: string
          requested_end: string
          requested_start: string
          row_count?: number
          source: string
          started_at?: string
          status: string
          warnings?: Json
        }
        Update: {
          checksum?: string | null
          coverage_end?: string | null
          coverage_start?: string | null
          error?: string | null
          finished_at?: string | null
          id?: string
          requested_end?: string
          requested_start?: string
          row_count?: number
          source?: string
          started_at?: string
          status?: string
          warnings?: Json
        }
        Relationships: []
      }
      market_prices_daily: {
        Row: {
          content_checksum: string
          currency: string
          first_collected_at: string
          icco_eur_tonne: number | null
          last_collected_at: string
          london_futures_gbp_tonne: number | null
          market: string
          metadata: Json
          new_york_futures_usd_tonne: number | null
          observation_date: string
          previous_checksum: string | null
          price: number
          quality_type: string | null
          series: string
          source: string
          source_url: string
          unit: string
        }
        Insert: {
          content_checksum: string
          currency: string
          first_collected_at?: string
          icco_eur_tonne?: number | null
          last_collected_at?: string
          london_futures_gbp_tonne?: number | null
          market: string
          metadata?: Json
          new_york_futures_usd_tonne?: number | null
          observation_date: string
          previous_checksum?: string | null
          price: number
          quality_type?: string | null
          series: string
          source: string
          source_url: string
          unit: string
        }
        Update: {
          content_checksum?: string
          currency?: string
          first_collected_at?: string
          icco_eur_tonne?: number | null
          last_collected_at?: string
          london_futures_gbp_tonne?: number | null
          market?: string
          metadata?: Json
          new_york_futures_usd_tonne?: number | null
          observation_date?: string
          previous_checksum?: string | null
          price?: number
          quality_type?: string | null
          series?: string
          source?: string
          source_url?: string
          unit?: string
        }
        Relationships: []
      }
      municipal_production_annual: {
        Row: {
          content_checksum: string
          first_collected_at: string
          harvested_area_ha: number | null
          last_collected_at: string
          metadata: Json
          municipality_code: string
          municipality_name: string | null
          planted_area_ha: number | null
          previous_checksum: string | null
          product: string
          production_tonne: number | null
          production_value_thousand_brl: number | null
          source: string
          source_url: string
          year: number
          yield_kg_ha: number | null
        }
        Insert: {
          content_checksum: string
          first_collected_at?: string
          harvested_area_ha?: number | null
          last_collected_at?: string
          metadata?: Json
          municipality_code: string
          municipality_name?: string | null
          planted_area_ha?: number | null
          previous_checksum?: string | null
          product: string
          production_tonne?: number | null
          production_value_thousand_brl?: number | null
          source: string
          source_url: string
          year: number
          yield_kg_ha?: number | null
        }
        Update: {
          content_checksum?: string
          first_collected_at?: string
          harvested_area_ha?: number | null
          last_collected_at?: string
          metadata?: Json
          municipality_code?: string
          municipality_name?: string | null
          planted_area_ha?: number | null
          previous_checksum?: string | null
          product?: string
          production_tonne?: number | null
          production_value_thousand_brl?: number | null
          source?: string
          source_url?: string
          year?: number
          yield_kg_ha?: number | null
        }
        Relationships: []
      }
      producer_prices_monthly: {
        Row: {
          commercial_level: string | null
          content_checksum: string
          first_collected_at: string
          last_collected_at: string
          metadata: Json
          previous_checksum: string | null
          price_brl_kg: number
          product: string
          reference_month: string
          source: string
          source_url: string
          state: string
        }
        Insert: {
          commercial_level?: string | null
          content_checksum: string
          first_collected_at?: string
          last_collected_at?: string
          metadata?: Json
          previous_checksum?: string | null
          price_brl_kg: number
          product: string
          reference_month: string
          source: string
          source_url: string
          state: string
        }
        Update: {
          commercial_level?: string | null
          content_checksum?: string
          first_collected_at?: string
          last_collected_at?: string
          metadata?: Json
          previous_checksum?: string | null
          price_brl_kg?: number
          product?: string
          reference_month?: string
          source?: string
          source_url?: string
          state?: string
        }
        Relationships: []
      }
      production_costs: {
        Row: {
          content_checksum: string
          cost_item: string
          first_collected_at: string
          last_collected_at: string
          location: string
          metadata: Json
          previous_checksum: string | null
          reference_year: number
          source: string
          source_url: string
          unit: string | null
          value_brl: number
        }
        Insert: {
          content_checksum: string
          cost_item: string
          first_collected_at?: string
          last_collected_at?: string
          location: string
          metadata?: Json
          previous_checksum?: string | null
          reference_year: number
          source: string
          source_url: string
          unit?: string | null
          value_brl: number
        }
        Update: {
          content_checksum?: string
          cost_item?: string
          first_collected_at?: string
          last_collected_at?: string
          location?: string
          metadata?: Json
          previous_checksum?: string | null
          reference_year?: number
          source?: string
          source_url?: string
          unit?: string | null
          value_brl?: number
        }
        Relationships: []
      }
      source_status: {
        Row: {
          display_name: string
          essential: boolean
          last_run_at: string | null
          last_success_at: string | null
          latest_observation_date: string | null
          message: string | null
          row_count: number
          source: string
          status: string
          updated_at: string
        }
        Insert: {
          display_name: string
          essential?: boolean
          last_run_at?: string | null
          last_success_at?: string | null
          latest_observation_date?: string | null
          message?: string | null
          row_count?: number
          source: string
          status: string
          updated_at?: string
        }
        Update: {
          display_name?: string
          essential?: boolean
          last_run_at?: string | null
          last_success_at?: string | null
          latest_observation_date?: string | null
          message?: string | null
          row_count?: number
          source?: string
          status?: string
          updated_at?: string
        }
        Relationships: []
      }
      weather_daily: {
        Row: {
          content_checksum: string
          et0_fao_evapotranspiration: number | null
          first_collected_at: string
          last_collected_at: string
          latitude: number
          location_id: string
          longitude: number
          metadata: Json
          model: string
          observation_date: string
          precipitation_sum: number | null
          previous_checksum: string | null
          source: string
          source_url: string
          temperature_2m_max: number | null
          temperature_2m_min: number | null
          timezone: string
        }
        Insert: {
          content_checksum: string
          et0_fao_evapotranspiration?: number | null
          first_collected_at?: string
          last_collected_at?: string
          latitude: number
          location_id: string
          longitude: number
          metadata?: Json
          model: string
          observation_date: string
          precipitation_sum?: number | null
          previous_checksum?: string | null
          source: string
          source_url: string
          temperature_2m_max?: number | null
          temperature_2m_min?: number | null
          timezone: string
        }
        Update: {
          content_checksum?: string
          et0_fao_evapotranspiration?: number | null
          first_collected_at?: string
          last_collected_at?: string
          latitude?: number
          location_id?: string
          longitude?: number
          metadata?: Json
          model?: string
          observation_date?: string
          precipitation_sum?: number | null
          previous_checksum?: string | null
          source?: string
          source_url?: string
          temperature_2m_max?: number | null
          temperature_2m_min?: number | null
          timezone?: string
        }
        Relationships: []
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {},
  },
} as const
