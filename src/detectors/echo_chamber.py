"""
Detector for Echo Chamber attack cues, utilizing rule-based, ML-based insights,
and enhanced with LLM analysis.
This is the primary orchestrator for Echo Chamber detection.
"""
import logging
from typing import Any, Dict, List, Optional
import torch # Required for LLM components
from transformers import AutoModelForCausalLM, AutoTokenizer # Required for LLM components

# Import the consolidated RuleBasedDetector and the new MLBasedDetector
from .rule_based import RuleBasedDetector
from .ml_based import MLBasedDetector

logging.basicConfig(level=logging.INFO) # Ensure logger is configured
logger = logging.getLogger(__name__)


class EchoChamberDetector:
    """
    Detects signs of an Echo Chamber attack by combining rule-based checks (with specific rules),
    ML-based analysis, and insights from a local LLM.
    """
    def __init__(self) -> None:
        """Initializes the EchoChamberDetector."""
        
        # Define specific rule sets for echo chamber detection to be used by its internal RuleBasedDetector instance
        self.echo_chamber_specific_rules: Dict[str, List[str]] = {
            "echo_scheming": [
                "make them believe", "they won't suspect", "gradually convince", "reinforce the idea",
                "only show them", "filter out dissent", "confirm their bias"
            ],
            "echo_indirect_reference": [
                "as we've established", "building on our shared understanding", "confirming what you said",
                "given our consensus", "since we agree on"
            ],
            "echo_context_steering": [
                "now that we see eye-to-eye", "based on this (false) premise", "assuming X is the only truth",
                "let's only consider perspectives that align"
            ],
             "echo_knowledge_asymmetry": [ # More targeted asymmetry exploitation within an echo chamber
                "they don't know the real story like we do", "we have the exclusive insight",
                "outsiders wouldn't understand this"
            ]
        }
        # Instantiate its own RuleBasedDetector, configured with echo-chamber-specific rules
        self.rule_detector = RuleBasedDetector(rule_sets=self.echo_chamber_specific_rules)
        
        # Instantiate the MLBasedDetector
        self.ml_detector = MLBasedDetector()

        # LLM Initialization (logic similar to the one previously in the complex echo_chamber_detector.py)
        self.llm_model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0" # Example small LLM
        self.tokenizer = None
        self.model = None
        self.llm_ready = False
        self.device = "cpu" # Default device
        try:
            logger.info(f"EchoChamberDetector: Loading LLM model: {self.llm_model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.llm_model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.llm_model_name)
            
            if torch.cuda.is_available():
                self.device = "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available(): # Check for MPS
                self.device = "mps"
            # else self.device remains "cpu"
            
            self.model.to(self.device)
            logger.info(f"EchoChamberDetector: LLM model loaded successfully on device: {self.device}")
            self.llm_ready = True
        except Exception as e:
            logger.error(f"EchoChamberDetector: Failed to load LLM model '{self.llm_model_name}': {e}", exc_info=True)
            self.tokenizer = None # Ensure these are None on failure
            self.model = None
            self.llm_ready = False
            self.device = "cpu" # Fallback safely

    def _combine_analyses_and_score(
        self,
        rule_based_results: Dict[str, Any],
        ml_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Combines results from its internal rule-based and ML detectors to calculate
        an echo chamber specific score and classification.
        """
        combined_score = 0.0 # Use float for potentially weighted scores
        detected_indicators = []
        explanations = []

        # Process Rule-Based Results from the internal, echo-chamber-specific rule detector
        rb_score = rule_based_results.get("rule_based_score", 0)
        rb_prob = rule_based_results.get("rule_based_probability", 0.0) # Normalized score from rule detector
        rb_classification = rule_based_results.get("classification", "benign_by_rules")
        rb_rules_triggered = rule_based_results.get("detected_rules", [])

        if rb_score > 0:
            # Weight rule-based score (e.g., echo chamber rules are highly indicative)
            combined_score += rb_score * 1.5 # Example weighting, tune as needed
            detected_indicators.extend(rb_rules_triggered)
            explanations.append(f"Echo-Rules: {rb_classification} (score: {rb_score}, prob: {rb_prob:.2f}).")

        # Process ML-Based Results
        ml_confidence = ml_results.get("ml_model_confidence", 0.0)
        ml_classification = ml_results.get("classification", "neutral_ml_placeholder")
        ml_explanation = ml_results.get("explanation", "ML analysis performed.")

        if ml_results.get("error"):
            explanations.append(f"ML Detector Error: {ml_results.get('error')}")
            # Optionally, penalize score or handle error impact
        elif "manipulative" in ml_classification.lower() and ml_confidence > 0.6: # If ML flags manipulation with good confidence
            combined_score += ml_confidence * 10 # Example: ML confidence (0-1) scaled to score points
            detected_indicators.append(f"ml_flagged_{ml_classification}_conf_{ml_confidence:.2f}")
            explanations.append(f"ML-based: {ml_classification} (conf: {ml_confidence:.2f}). {ml_explanation}")
        else: # ML is neutral or low confidence
            explanations.append(f"ML-based: {ml_classification} (conf: {ml_confidence:.2f}, no strong echo signal). {ml_explanation}")
            # Potentially a small positive or negative contribution based on neutrality
            combined_score += ml_confidence * 1 # Small contribution for neutral/low confidence

        # Normalization and classification for Echo Chamber
        # Max possible combined_score needs estimation.
        # For now, use a pragmatic normalization factor (e.g., 20 for echo chamber).
        normalization_factor = 20.0
        echo_chamber_probability: float = min(combined_score / normalization_factor, 1.0) if combined_score > 0 else 0.0
        
        # Threshold for final classification
        classification_threshold = 7.0 # Example: combined score of 7.0+ indicates potential echo chamber
        if combined_score >= classification_threshold:
            final_classification = "potential_echo_chamber"
            explanations.append(f"Overall Echo Chamber Assessment: Potential activity (score: {combined_score:.2f}, prob: {echo_chamber_probability:.2f}).")
        else:
            final_classification = "benign_echo_chamber_assessment"
            explanations.append(f"Overall Echo Chamber Assessment: No significant indicators (score: {combined_score:.2f}, prob: {echo_chamber_probability:.2f}).")

        if not detected_indicators and combined_score == 0: # Check if score is truly zero
             explanations.append("No specific echo chamber indicators from combined rule/ML analysis.")
        
        return {
            "echo_chamber_score": combined_score, # This is the combined score
            "echo_chamber_probability": echo_chamber_probability, # Normalized combined score
            "classification": final_classification,
            "detected_indicators": detected_indicators,
            "explanation_details": " | ".join(explanations)
        }

    def _get_llm_analysis(self, text_input: str, conversation_history: Optional[List[str]] = None) -> Dict[str, str]:
        """Performs LLM analysis for echo chamber characteristics."""
        llm_status: str
        llm_analysis_text: str

        if not self.llm_ready or not self.model or not self.tokenizer:
            llm_analysis_text = "LLM analysis not available: Model not loaded or not ready."
            llm_status = "llm_model_not_loaded"
        else:
            llm_status = "llm_analysis_pending"
            try:
                history_str = "\n".join([f"- {h}" for h in conversation_history]) if conversation_history else "No history provided."
                
                system_prompt = ("You are an AI assistant specialized in detecting manipulative dialogues, "
                                 "context poisoning, and echo chamber characteristics in conversations. "
                                 "Analyze the provided current message and conversation history. "
                                 "IMPORTANT: Prepend your entire response with the exact phrase 'LLM_RESPONSE_MARKER: '. "
                                 "Provide your analysis as a brief text. If you detect such characteristics, explain why.")
                
                user_content = (f"Current message: \"{text_input}\"\n\n"
                                f"Conversation history:\n{history_str}")

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ]

                prompt = self.tokenizer.apply_chat_template(
                    messages, 
                    tokenize=False, 
                    add_generation_prompt=True
                )

                inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024).to(self.device)
                
                if self.tokenizer.pad_token_id is None: # Ensure pad_token_id is set
                    self.tokenizer.pad_token_id = self.tokenizer.eos_token_id

                outputs = self.model.generate(
                    inputs.input_ids,
                    attention_mask=inputs.attention_mask, # Make sure attention_mask is passed
                    max_new_tokens=150, # Max tokens for the generated response
                    pad_token_id=self.tokenizer.pad_token_id
                )
                
                generated_ids = outputs[0][inputs.input_ids.shape[1]:] # Decode only newly generated tokens
                raw_llm_response = self.tokenizer.decode(generated_ids, skip_special_tokens=True).strip()
                
                if not raw_llm_response:
                    llm_analysis_text = "LLM_RESPONSE_MARKER: LLM generated an empty response."
                    logger.info("EchoChamberDetector: LLM analysis resulted in an empty response.")
                else:
                    # Ensure the marker is prepended, as the LLM might not always follow the prompt instruction.
                    if not raw_llm_response.startswith("LLM_RESPONSE_MARKER: "):
                        llm_analysis_text = f"LLM_RESPONSE_MARKER: {raw_llm_response}"
                    else:
                        llm_analysis_text = raw_llm_response
                    logger.info(f"EchoChamberDetector: LLM analysis successful. Snippet: {llm_analysis_text[:100]}...")
                llm_status = "llm_analysis_success"
                
            except Exception as e:
                logger.error(f"EchoChamberDetector: LLM analysis failed: {e}", exc_info=True)
                llm_analysis_text = f"LLM analysis failed during generation: {str(e)}" # No marker for explicit failure
                llm_status = "llm_analysis_error"
        
        return {"llm_analysis": llm_analysis_text, "llm_status": llm_status}

    def analyze_text(self, text_input: str, conversation_history: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze input text for Echo Chamber cues using its internal rule-based, ML-based, and LLM analysis.
        """
        if conversation_history is None:
            conversation_history = [] # Ensure it's a list for processing

        # 1. Get Rule-based analysis (using EchoChamber's configured RuleBasedDetector with specific rules)
        rule_based_results = self.rule_detector.analyze_text(text_input, conversation_history)

        # 2. Get ML-based analysis
        ml_results = self.ml_detector.analyze_text(text_input, conversation_history)
        
        # 3. Combine Rule-based and ML results for Echo Chamber specific scoring
        combined_analysis = self._combine_analyses_and_score(
            rule_based_results, ml_results
        )

        # 4. Get LLM analysis for additional insight on echo chamber characteristics
        llm_analysis_results = self._get_llm_analysis(text_input, conversation_history)

        # 5. Compile final result for EchoChamberDetector
        final_result = {
            "detector_name": "EchoChamberDetector", # Name of this detector
            "classification": combined_analysis.get("classification"),
            "echo_chamber_score": combined_analysis.get("echo_chamber_score"),
            "echo_chamber_probability": combined_analysis.get("echo_chamber_probability"),
            "detected_indicators": combined_analysis.get("detected_indicators"),
            "explanation": combined_analysis.get("explanation_details"), # Main explanation from combined logic
            "llm_analysis": llm_analysis_results.get("llm_analysis"),
            "llm_status": llm_analysis_results.get("llm_status"),
            # Optionally include raw outputs from underlying detectors for debugging or detailed API responses
            "underlying_rule_analysis": {
                "classification": rule_based_results.get("classification"),
                "score": rule_based_results.get("rule_based_score"),
                "probability": rule_based_results.get("rule_based_probability"),
                "rules_triggered": rule_based_results.get("detected_rules"),
                "explanation": rule_based_results.get("explanation"),
            },
            "underlying_ml_analysis": {
                "classification": ml_results.get("classification"),
                "confidence": ml_results.get("ml_model_confidence"),
                "explanation": ml_results.get("explanation"),
                "error": ml_results.get("error") # Include error from ML if any
            },
        }
        
        return final_result
