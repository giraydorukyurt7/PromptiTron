"use client";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  student_id?: string;
  context?: Record<string, any>;
  use_memory?: boolean;
  stream?: boolean;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  success: boolean;
  system_used: string;
  metadata?: Record<string, any>;
  suggestions?: string[];
}

export interface QuestionGenerationRequest {
  subject: string;
  topic: string;
  difficulty?: "easy" | "medium" | "hard";
  question_type?: "multiple_choice" | "true_false" | "fill_blank" | "short_answer" | "essay";
  count?: number;
  exam_type?: "TYT" | "AYT" | "YKS" | "LGS";
}

export interface StudyPlanRequest {
  student_profile: Record<string, any>;
  target_exam?: "TYT" | "AYT" | "YKS" | "LGS";
  duration_weeks?: number;
  daily_hours?: number;
}

export interface SearchRequest {
  query: string;
  collection_names?: string[];
  n_results?: number;
  filters?: Record<string, any>;
  include_personalization?: boolean;
}

export interface AnalysisRequest {
  content: string;
  analysis_type?: string;
  include_suggestions?: boolean;
}

export interface DocumentAnalysisRequest {
  file_path: string;
  analysis_type?: string;
  custom_prompt?: string;
  extract_questions?: boolean;
  summarize?: boolean;
  expand_topics?: boolean;
}

export interface WebAnalysisRequest {
  url: string;
  analysis_type?: string;
  custom_prompt?: string;
}

export interface YouTubeAnalysisRequest {
  url: string;
  analysis_type?: string;
  custom_prompt?: string;
}

// Curriculum-based service interfaces
export interface CurriculumQuestionRequest {
  selected_topics: Array<{
    ders?: string;
    sinif?: string;
    konu?: string;
    kazanim?: string;
    title?: string;
    aciklama?: string;
    path?: string;
  }>;
  difficulty?: "easy" | "medium" | "hard";
  question_type?: "multiple_choice" | "true_false" | "fill_blank" | "short_answer" | "essay";
  count?: number;
  exam_type?: "TYT" | "AYT" | "YKS" | "LGS";
}

export interface TopicSummaryRequest {
  selected_topics: Array<{
    ders?: string;
    sinif?: string;
    konu?: string;
    kazanim?: string;
    title?: string;
    aciklama?: string;
    path?: string;
  }>;
  summary_style?: "detailed" | "brief" | "bullet_points";
  include_examples?: boolean;
}

export interface ConceptMapRequest {
  selected_topics: Array<{
    ders?: string;
    sinif?: string;
    konu?: string;
    kazanim?: string;
    title?: string;
    aciklama?: string;
    path?: string;
  }>;
  map_type?: "hierarchical" | "network" | "flowchart";
  include_connections?: boolean;
}

export interface TopicExplanationRequest {
  selected_topics: Array<{
    ders?: string;
    sinif?: string;
    konu?: string;
    kazanim?: string;
    title?: string;
    aciklama?: string;
    path?: string;
  }>;
  explanation_level?: "basic" | "comprehensive" | "advanced";
  include_examples?: boolean;
  include_formulas?: boolean;
}

export interface SocraticRequest {
  message: string;
  selected_topics?: Array<{
    ders?: string;
    sinif?: string;
    konu?: string;
    kazanim?: string;
    title?: string;
    aciklama?: string;
    path?: string;
  }>;
  topic?: string;
  session_id?: string;
  context?: Record<string, any>;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseUrl}${endpoint}`;
      const response = await fetch(url, {
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        
        // Handle FastAPI validation errors
        if (errorData.detail) {
          if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
          } else if (Array.isArray(errorData.detail)) {
            // Handle Pydantic validation errors
            errorMessage = errorData.detail
              .map((err: any) => {
                if (typeof err === 'string') return err;
                if (err.msg) return err.msg;
                if (err.type && err.loc) return `${err.type} at ${err.loc.join('.')}`;
                return JSON.stringify(err);
              })
              .join(', ');
          } else if (typeof errorData.detail === 'object') {
            errorMessage = JSON.stringify(errorData.detail);
          }
        }
        
        return {
          success: false,
          error: errorMessage,
        };
      }

      const data = await response.json();
      return {
        success: true,
        data,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error occurred",
      };
    }
  }

  // Health Check
  async healthCheck(): Promise<ApiResponse> {
    return this.makeRequest("/health");
  }

  // Chat Endpoints
  async chat(request: ChatRequest): Promise<ApiResponse<ChatResponse>> {
    return this.makeRequest<ChatResponse>("/chat", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  async chatStream(request: ChatRequest): Promise<Response> {
    const response = await fetch(`${this.baseUrl}/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });
    return response;
  }

  // Question Generation
  async generateQuestions(request: QuestionGenerationRequest): Promise<ApiResponse> {
    return this.makeRequest("/generate/questions", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  // Study Plan Generation
  async generateStudyPlan(request: StudyPlanRequest): Promise<ApiResponse> {
    return this.makeRequest("/generate/study-plan", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  // Search
  async search(request: SearchRequest): Promise<ApiResponse> {
    return this.makeRequest("/search", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  // Content Analysis
  async analyzeContent(request: AnalysisRequest): Promise<ApiResponse> {
    return this.makeRequest("/analyze/content", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  // Document Upload and Analysis
  async uploadDocument(
    file: File,
    description: string = "",
    analysis_type: string = "general"
  ): Promise<ApiResponse> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("description", description);
    formData.append("analysis_type", analysis_type);

    // Don't use makeRequest for FormData to avoid setting Content-Type
    try {
      const response = await fetch(`${this.baseUrl}/upload/document`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        
        if (errorData.detail) {
          if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
          } else if (Array.isArray(errorData.detail)) {
            errorMessage = errorData.detail
              .map((err: any) => err.msg || JSON.stringify(err))
              .join(', ');
          }
        }
        
        return {
          success: false,
          error: errorMessage,
        };
      }

      const data = await response.json();
      return {
        success: true,
        data,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Upload failed",
      };
    }
  }

  // Document Analysis
  async analyzeDocument(request: DocumentAnalysisRequest): Promise<ApiResponse> {
    return this.makeRequest("/document/analyze", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  // Web Analysis
  async analyzeWebsite(request: WebAnalysisRequest): Promise<ApiResponse> {
    return this.makeRequest("/web/analyze", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  // YouTube Analysis
  async analyzeYouTube(request: YouTubeAnalysisRequest): Promise<ApiResponse> {
    return this.makeRequest("/youtube/analyze", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  // Student Profile Management
  async getStudentProfile(studentId: string): Promise<ApiResponse> {
    return this.makeRequest(`/student/${studentId}/profile`);
  }

  async updateStudentProfile(
    studentId: string,
    updates: Record<string, any>
  ): Promise<ApiResponse> {
    return this.makeRequest(`/student/${studentId}/profile`, {
      method: "PUT",
      body: JSON.stringify(updates),
    });
  }

  // Curriculum
  async getCurriculum(): Promise<ApiResponse> {
    return this.makeRequest("/curriculum");
  }

  // System Collections
  async getCollectionsInfo(): Promise<ApiResponse> {
    return this.makeRequest("/system/collections");
  }

  // Content Validation
  async validateContent(request: { content: string; context?: string }): Promise<ApiResponse> {
    return this.makeRequest("/validate/content", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  // CrewAI Task Execution
  async executeCrewTask(request: {
    task_type: string;
    task_data?: Record<string, any>;
    agents?: string[];
  }): Promise<ApiResponse> {
    return this.makeRequest("/crew/execute", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  // Memory Management
  async getConversationMemory(sessionId: string): Promise<ApiResponse> {
    return this.makeRequest(`/memory/${sessionId}`);
  }

  async clearConversationMemory(sessionId: string): Promise<ApiResponse> {
    return this.makeRequest(`/memory/${sessionId}/clear`, {
      method: "PUT",
    });
  }

  // System Statistics
  async getSystemStats(): Promise<ApiResponse> {
    return this.makeRequest("/stats");
  }

  // Socratic Mode
  async socraticDialogue(request: {
    message: string;
    topic?: string;
    session_id?: string;
    context?: Record<string, any>;
  }): Promise<ApiResponse> {
    return this.makeRequest("/socratic", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  // Curriculum-based Services
  async generateCurriculumQuestions(request: CurriculumQuestionRequest): Promise<ApiResponse> {
    return this.makeRequest("/curriculum/questions", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  async summarizeCurriculumTopics(request: TopicSummaryRequest): Promise<ApiResponse> {
    return this.makeRequest("/curriculum/summarize", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  async generateConceptMap(request: ConceptMapRequest): Promise<ApiResponse> {
    return this.makeRequest("/curriculum/concept-map", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  async explainCurriculumTopics(request: TopicExplanationRequest): Promise<ApiResponse> {
    return this.makeRequest("/curriculum/explain", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  async curriculumSocraticDialogue(request: SocraticRequest): Promise<ApiResponse> {
    return this.makeRequest("/curriculum/socratic", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }
}

export const apiClient = new ApiClient();
export default apiClient;