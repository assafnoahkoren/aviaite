export interface PageRange {
  end_in_page: number;
  page_number: number;
  start_in_page: number;
  page_text_length: number;
}

export interface ChunkMetadata {
  pages: number[];
  end_char: number;
  num_words: number;
  chunk_size: number;
  start_char: number;
  chunk_index: number;
  page_ranges: PageRange[];
  is_last_chunk: boolean;
  num_sentences: number;
  is_first_chunk: boolean;
  spans_multiple_pages: boolean;
}

export interface SearchResult {
  chunk_id: number;
  chunk_text: string;
  similarity: number;
  metadata: ChunkMetadata;
}

export interface SearchAnalysis {
  answer: string;
}

export interface SemanticSearchResponse {
  results: SearchResult[];
  total_results: number;
  query: string;
  analysis: SearchAnalysis;
} 