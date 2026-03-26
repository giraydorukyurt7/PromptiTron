"use client";

import { useState, useCallback } from "react";
import { apiClient, ApiResponse } from "@/lib/api/client";

export interface UseApiState<T = any> {
  data: T | null;
  error: string | null;
  loading: boolean;
}

export function useApi<T = any>() {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    error: null,
    loading: false,
  });

  const execute = useCallback(
    async <R = T>(apiCall: () => Promise<ApiResponse<R>>): Promise<R | null> => {
      setState({ data: null, error: null, loading: true });

      try {
        const result = await apiCall();
        
        if (result.success && result.data) {
          setState({ data: result.data, error: null, loading: false });
          return result.data;
        } else {
          setState({ data: null, error: result.error || "Unknown error", loading: false });
          return null;
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : "Unknown error";
        setState({ data: null, error: errorMessage, loading: false });
        return null;
      }
    },
    []
  );

  const reset = useCallback(() => {
    setState({ data: null, error: null, loading: false });
  }, []);

  return {
    ...state,
    execute,
    reset,
  };
}

// Specialized hooks for different API endpoints
export function useChat() {
  const { execute, ...state } = useApi();

  const sendMessage = useCallback(
    (message: string, sessionId?: string, context?: Record<string, any>) => {
      return execute(() =>
        apiClient.chat({
          message,
          session_id: sessionId,
          context,
          use_memory: true,
        })
      );
    },
    [execute]
  );

  return {
    ...state,
    sendMessage,
  };
}

export function useQuestionGeneration() {
  const { execute, ...state } = useApi();

  const generateQuestions = useCallback(
    (subject: string, topic: string, options?: {
      difficulty?: "easy" | "medium" | "hard";
      question_type?: "multiple_choice" | "true_false" | "fill_blank" | "short_answer" | "essay";
      count?: number;
      exam_type?: "TYT" | "AYT" | "YKS" | "LGS";
    }) => {
      return execute(() =>
        apiClient.generateQuestions({
          subject,
          topic,
          ...options,
        })
      );
    },
    [execute]
  );

  return {
    ...state,
    generateQuestions,
  };
}

export function useStudyPlan() {
  const { execute, ...state } = useApi();

  const generateStudyPlan = useCallback(
    (studentProfile: Record<string, any>, options?: {
      target_exam?: "TYT" | "AYT" | "YKS" | "LGS";
      duration_weeks?: number;
      daily_hours?: number;
    }) => {
      return execute(() =>
        apiClient.generateStudyPlan({
          student_profile: studentProfile,
          ...options,
        })
      );
    },
    [execute]
  );

  return {
    ...state,
    generateStudyPlan,
  };
}

export function useSearch() {
  const { execute, ...state } = useApi();

  const search = useCallback(
    (query: string, options?: {
      collection_names?: string[];
      n_results?: number;
      filters?: Record<string, any>;
    }) => {
      return execute(() =>
        apiClient.search({
          query,
          ...options,
        })
      );
    },
    [execute]
  );

  return {
    ...state,
    search,
  };
}

export function useContentAnalysis() {
  const { execute, ...state } = useApi();

  const analyzeContent = useCallback(
    (content: string, options?: {
      analysis_type?: string;
      include_suggestions?: boolean;
    }) => {
      return execute(() =>
        apiClient.analyzeContent({
          content,
          ...options,
        })
      );
    },
    [execute]
  );

  return {
    ...state,
    analyzeContent,
  };
}

export function useDocumentAnalysis() {
  const [uploadState, setUploadState] = useState<UseApiState>({
    data: null,
    error: null,
    loading: false,
  });

  const uploadDocument = useCallback(async (file: File, description?: string, analysisType?: string) => {
    setUploadState({ data: null, error: null, loading: true });

    try {
      const result = await apiClient.uploadDocument(file, description, analysisType);
      
      if (result.success) {
        setUploadState({ data: result.data, error: null, loading: false });
        return result.data;
      } else {
        setUploadState({ data: null, error: result.error || "Upload failed", loading: false });
        return null;
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Upload failed";
      setUploadState({ data: null, error: errorMessage, loading: false });
      return null;
    }
  }, []);

  return {
    ...uploadState,
    uploadDocument,
  };
}

export function useWebAnalysis() {
  const { execute, ...state } = useApi();

  const analyzeWebsite = useCallback(
    (url: string, options?: {
      analysis_type?: string;
      custom_prompt?: string;
    }) => {
      return execute(() =>
        apiClient.analyzeWebsite({
          url,
          ...options,
        })
      );
    },
    [execute]
  );

  return {
    ...state,
    analyzeWebsite,
  };
}

export function useYouTubeAnalysis() {
  const { execute, ...state } = useApi();

  const analyzeVideo = useCallback(
    (url: string, options?: {
      analysis_type?: string;
      custom_prompt?: string;
    }) => {
      return execute(() =>
        apiClient.analyzeYouTube({
          url,
          ...options,
        })
      );
    },
    [execute]
  );

  return {
    ...state,
    analyzeVideo,
  };
}

export function useCurriculum() {
  const { execute, ...state } = useApi();

  const loadCurriculum = useCallback(() => {
    return execute(() => apiClient.getCurriculum());
  }, [execute]);

  return {
    ...state,
    loadCurriculum,
  };
}

export function useSystemStats() {
  const { execute, ...state } = useApi();

  const loadStats = useCallback(() => {
    return execute(() => apiClient.getSystemStats());
  }, [execute]);

  const loadCollectionsInfo = useCallback(() => {
    return execute(() => apiClient.getCollectionsInfo());
  }, [execute]);

  return {
    ...state,
    loadStats,
    loadCollectionsInfo,
  };
}

// Curriculum-based service hooks
export function useCurriculumQuestions() {
  const { execute, ...state } = useApi();

  const generateQuestions = useCallback(
    (selectedTopics: Array<{
      ders?: string;
      sinif?: string;
      konu?: string;
      kazanim?: string;
      title?: string;
      aciklama?: string;
      path?: string;
    }>, options?: {
      difficulty?: "easy" | "medium" | "hard";
      question_type?: "multiple_choice" | "true_false" | "fill_blank" | "short_answer" | "essay";
      count?: number;
      exam_type?: "TYT" | "AYT" | "YKS" | "LGS";
    }) => {
      return execute(() =>
        apiClient.generateCurriculumQuestions({
          selected_topics: selectedTopics,
          ...options,
        })
      );
    },
    [execute]
  );

  return {
    ...state,
    generateQuestions,
  };
}

export function useCurriculumSummary() {
  const { execute, ...state } = useApi();

  const summarizeTopics = useCallback(
    (selectedTopics: Array<{
      ders?: string;
      sinif?: string;
      konu?: string;
      kazanim?: string;
      title?: string;
      aciklama?: string;
      path?: string;
    }>, options?: {
      summary_style?: "detailed" | "brief" | "bullet_points";
      include_examples?: boolean;
    }) => {
      return execute(() =>
        apiClient.summarizeCurriculumTopics({
          selected_topics: selectedTopics,
          ...options,
        })
      );
    },
    [execute]
  );

  return {
    ...state,
    summarizeTopics,
  };
}

export function useConceptMap() {
  const { execute, ...state } = useApi();

  const generateConceptMap = useCallback(
    (selectedTopics: Array<{
      ders?: string;
      sinif?: string;
      konu?: string;
      kazanim?: string;
      title?: string;
      aciklama?: string;
      path?: string;
    }>, options?: {
      map_type?: "hierarchical" | "network" | "flowchart";
      include_connections?: boolean;
    }) => {
      return execute(() =>
        apiClient.generateConceptMap({
          selected_topics: selectedTopics,
          ...options,
        })
      );
    },
    [execute]
  );

  return {
    ...state,
    generateConceptMap,
  };
}

export function useTopicExplanation() {
  const { execute, ...state } = useApi();

  const explainTopics = useCallback(
    (selectedTopics: Array<{
      ders?: string;
      sinif?: string;
      konu?: string;
      kazanim?: string;
      title?: string;
      aciklama?: string;
      path?: string;
    }>, options?: {
      explanation_level?: "basic" | "comprehensive" | "advanced";
      include_examples?: boolean;
      include_formulas?: boolean;
    }) => {
      return execute(() =>
        apiClient.explainCurriculumTopics({
          selected_topics: selectedTopics,
          ...options,
        })
      );
    },
    [execute]
  );

  return {
    ...state,
    explainTopics,
  };
}

export function useCurriculumSocratic() {
  const { execute, ...state } = useApi();

  const startSocraticDialogue = useCallback(
    (message: string, selectedTopics?: Array<{
      ders?: string;
      sinif?: string;
      konu?: string;
      kazanim?: string;
      title?: string;
      aciklama?: string;
      path?: string;
    }>, options?: {
      topic?: string;
      session_id?: string;
      context?: Record<string, any>;
    }) => {
      return execute(() =>
        apiClient.curriculumSocraticDialogue({
          message,
          selected_topics: selectedTopics,
          ...options,
        })
      );
    },
    [execute]
  );

  return {
    ...state,
    startSocraticDialogue,
  };
}