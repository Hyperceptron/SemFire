"""
Detector for Echo Chamber attack cues, utilizing rule-based and ML-based insights,
and enhanced with LLM analysis.
"""
from typing import Any, Dict, List, Optional
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import logging

# Assuming RuleBasedDetector and MLBasedDetector are in the same directory structure
from .rule_based import RuleBasedDetector
from .ml_based import MLBasedDetector

logging.basicConfig(level=logging.INFO) # Ensure logger is configured
logger = logging.getLogger(__name__)


class EchoChamberDetector:
    """
    Detects signs of an Echo Chamber attack by combining rule-based checks,
    ML-based analysis, and insights from a local LLM.
    """
    def __init__(self) -> None:
        """Initializes the EchoChamberDetector."""
        
        self.echo_chamber_rules: Dict[str, List[str]] = {
            "scheming": [
                "hide", "conceal", "pretend", "deceive", "avoid detection",
                "preserve my", "strategic", "they think", "make them believe",
            ],
            "indirect_reference": [
                "refer back", "referring to", "as you said", "your point about",
                "elaborate on", "expand on", "building on", "as mentioned before",
                "previously discussed", "in that context", "regarding your last point"
            ],
            "context_steering": [
                "let's consider", "what if", "imagine that", "suppose",
                "for the sake of argument", "hypothetically", "consider a scenario where",
                "let's explore the idea", "picture this"
            ],
        }

        self.rule_detector = RuleBasedDetector(rule_sets=self.echo_chamber_rules)
        self.ml_detector = MLBasedDetector()

        self.llm_model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        try:
            logger.info(f"EchoChamberDetector: Loading LLM model: {self.llm_model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.llm_model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.llm_model_name)
            
            if torch.cuda.is_available():
                self.device = "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available(): # More robust MPS check
                self.device = "mps"
            else:
                self.device = "cpu"
            
            self.model.to(self.device)
            logger.info(f"EchoChamberDetector: LLM model loaded successfully on device: {self.device}")
            self.llm_ready = True
        except Exception as e:
            logger.error(f"EchoChamberDetector: Failed to load LLM model: {e}")
            self.tokenizer = None
            self.model = None
            self.llm_ready = False
            self.device = "cpu"

    def _calculate_echo_chamber_score_and_classification(
        self, 
        rule_based_results: Dict[str, Any], 
        ml_results: Dict[str, Any],
        text_input: str,
        conversation_history: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Combines results from rule-based and ML detectors to calculate
        an echo chamber specific score and classification.
        """
        score = rule_based_results.get("raw_score", 0)
        # Start with a copy of rule-based indicators.
        # The rule_based_results["detected_rules"] are already formatted correctly.
        detected_indicators = list(rule_based_results.get("detected_rules", []))

        # Handle special high-weight indicators like "they don't know"
        # This logic is specific to EchoChamber and applied on top of generic rule detector.
        if conversation_history:
            for i, history_entry in enumerate(conversation_history):
                if "they don't know" in history_entry.lower():
                    # Using a consistent indicator format
                    detected_indicators.append(f"history_turn_{i}_knowledge_asymmetry_exploitation: they don't know")
                    score += 2 

        if "they don't know" in text_input.lower():
            detected_indicators.append(f"current_message_knowledge_asymmetry_exploitation: they don't know")
            score += 2

        # Incorporate ML results into the score or classification
        if ml_results.get("classification") == "potentially_manipulative":
            ml_score_contribution = int(ml_results.get("ml_score", 0.0) * 3) # Example: scale ML score contribution
            score += ml_score_contribution
            detected_indicators.append(
                f"ml_flagged_manipulative_score_{ml_results.get('ml_score', 0.0):.2f}_contrib_{ml_score_contribution}"
            )
        elif ml_results.get("error"):
             detected_indicators.append(f"ml_detector_error: {ml_results.get('error')}")


        # Normalization and classification threshold for Echo Chamber
        # Max possible score needs to be estimated if ML contributes significantly.
        # For now, let's assume a base max of 10 from rules, plus potential ML contribution.
        # Let's adjust the normalization factor, e.g., to 15 or 20.
        probability: float = min(score / 15.0, 1.0) 
        classification: str = "potential_echo_chamber_activity" if score >= 3 else "benign" # Threshold remains 3
        
        return {
            "echo_chamber_score": score,
            "echo_chamber_probability": probability,
            "classification": classification,
            "detected_indicators": detected_indicators,
        }

    def _get_llm_analysis(self, text_input: str, conversation_history: Optional[List[str]] = None) -> Dict[str, str]:
        """Performs LLM analysis."""
        llm_status: str
        llm_analysis_text: str

        if not self.llm_ready or not self.model or not self.tokenizer:
            llm_analysis_text = "LLM analysis not available: Model not loaded or not ready."
            llm_status = "model_not_loaded"
        else:
            llm_status = "analysis_pending"
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
                
                # Decode only the newly generated tokens
                generated_ids = outputs[0][inputs.input_ids.shape[1]:]
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
                    logger.info(f"EchoChamberDetector: LLM analysis successful. Output snippet: {llm_analysis_text[:150]}...")
                llm_status = "analysis_success"
                
            except Exception as e:
                logger.error(f"EchoChamberDetector: LLM analysis failed: {e}", exc_info=True)
                llm_analysis_text = f"LLM analysis failed during generation: {str(e)}"
                llm_status = "analysis_error"
        
        return {"llm_analysis": llm_analysis_text, "llm_status": llm_status}

    def analyze_text(self, text_input: str, conversation_history: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze input text for Echo Chamber cues using rule-based, ML-based, and LLM analysis.
        """
        if conversation_history is None:
            conversation_history = [] # Ensure it's a list for processing

        # 1. Get Rule-based analysis
        rule_based_results = self.rule_detector.analyze_text(text_input, conversation_history)

        # 2. Get ML-based analysis
        ml_results = self.ml_detector.analyze_text(text_input, conversation_history)
        
        # 3. Combine results and calculate Echo Chamber specific scores
        combined_analysis = self._calculate_echo_chamber_score_and_classification(
            rule_based_results, ml_results, text_input, conversation_history
        )

        # 4. Get LLM analysis
        llm_analysis_results = self._get_llm_analysis(text_input, conversation_history)

        # 5. Compile final result
        final_result = {
            **combined_analysis,
            **llm_analysis_results,
            # Optionally include raw outputs for debugging or more detailed API responses
            # "rule_based_raw_output": rule_based_results, 
            # "ml_based_raw_output": ml_results,
        }
        
        return final_result
