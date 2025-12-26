# Copyright (C) 2025 AIDC-AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
TTS (Text-to-Speech) Service - Supports both local and ComfyUI inference
"""

import os
import uuid
import json
from pathlib import Path
from typing import Optional

from comfykit import ComfyKit
from loguru import logger

from pixelle_video.services.comfy_base_service import ComfyBaseService
from pixelle_video.utils.tts_util import edge_tts
from pixelle_video.tts_voices import speed_to_rate


class TTSService(ComfyBaseService):
    """
    TTS (Text-to-Speech) service - Workflow-based
    
    Uses ComfyKit to execute TTS workflows.
    
    Usage:
        # Use default workflow
        audio_path = await pixelle_video.tts(text="Hello, world!")
        
        # Use specific workflow
        audio_path = await pixelle_video.tts(
            text="你好，世界！",
            workflow="tts_edge.json"
        )
        
        # List available workflows
        workflows = pixelle_video.tts.list_workflows()
    """
    
    WORKFLOW_PREFIX = "tts_"
    DEFAULT_WORKFLOW = None  # No hardcoded default, must be configured
    WORKFLOWS_DIR = "workflows"
    
    def __init__(self, config: dict, core=None):
        """
        Initialize TTS service
        
        Args:
            config: Full application config dict
            core: PixelleVideoCore instance (for accessing shared ComfyKit)
        """
        super().__init__(config, service_name="tts", core=core)
    
    def _find_comfyui_input_dir(self, workflow_path: str = None) -> Optional[str]:
        """
        Find ComfyUI input directory using multiple strategies
        
        Args:
            workflow_path: Optional workflow file path for relative path lookup
            
        Returns:
            ComfyUI input directory path if found, None otherwise
        """
        # Strategy 1: Environment variable
        comfyui_path = os.getenv("COMFYUI_PATH") or os.getenv("COMFYUI_ROOT")
        if comfyui_path:
            input_dir = os.path.join(comfyui_path, "input")
            if os.path.exists(input_dir):
                logger.debug(f"Found ComfyUI input directory via environment variable: {os.path.abspath(input_dir)}")
                return os.path.abspath(input_dir)
        
        # Strategy 2: From comfyui_url if it's a local path
        comfyui_url = (
            self.global_config.get("comfyui_url")
            or os.getenv("COMFYUI_BASE_URL")
            or "http://127.0.0.1:8188"
        )
        # If comfyui_url is a file:// URL or local path, extract the path
        if comfyui_url.startswith("file://"):
            comfyui_path = comfyui_url[7:]  # Remove "file://" prefix
            input_dir = os.path.join(comfyui_path, "input")
            if os.path.exists(input_dir):
                logger.debug(f"Found ComfyUI input directory via file:// URL: {os.path.abspath(input_dir)}")
                return os.path.abspath(input_dir)
        elif not comfyui_url.startswith(("http://", "https://")):
            # Assume it's a local path
            if os.path.exists(comfyui_url):
                input_dir = os.path.join(comfyui_url, "input")
                if os.path.exists(input_dir):
                    logger.debug(f"Found ComfyUI input directory via local path: {os.path.abspath(input_dir)}")
                    return os.path.abspath(input_dir)
        
        # Strategy 3: Relative path from workflow file
        if workflow_path:
            possible_paths = [
                os.path.join(os.path.dirname(workflow_path), "..", "..", "ComfyUI", "input"),
                os.path.join(os.path.dirname(workflow_path), "..", "..", "..", "ComfyUI", "input"),
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(workflow_path))), "ComfyUI", "input"),
            ]
            for path in possible_paths:
                abs_path = os.path.abspath(path)
                if os.path.exists(abs_path):
                    logger.debug(f"Found ComfyUI input directory via relative path: {abs_path}")
                    return abs_path
        
        # Strategy 4: Common installation locations
        common_paths = [
            os.path.join(os.path.expanduser("~"), "ComfyUI", "input"),
            os.path.join("C:", "ComfyUI", "input"),
            os.path.join("D:", "ComfyUI", "input"),
            os.path.join("F:", "ComfyUI", "input"),
        ]
        for path in common_paths:
            if os.path.exists(path):
                logger.debug(f"Found ComfyUI input directory in common location: {os.path.abspath(path)}")
                return os.path.abspath(path)
        
        logger.warning("Could not find ComfyUI input directory using any strategy. Set COMFYUI_PATH environment variable to specify the path.")
        return None
    
    
    async def __call__(
        self,
        text: str,
        workflow: Optional[str] = None,
        # ComfyUI connection (optional overrides)
        comfyui_url: Optional[str] = None,
        runninghub_api_key: Optional[str] = None,
        # TTS parameters
        voice: Optional[str] = None,
        speed: Optional[float] = None,
        # Inference mode override
        inference_mode: Optional[str] = None,
        # Output path
        output_path: Optional[str] = None,
        **params
    ) -> str:
        """
        Generate speech using local Edge TTS or ComfyUI workflow
        
        Args:
            text: Text to convert to speech
            workflow: Workflow filename (for ComfyUI mode, default: from config)
            comfyui_url: ComfyUI URL (optional, overrides config)
            runninghub_api_key: RunningHub API key (optional, overrides config)
            voice: Voice ID (for local mode: Edge TTS voice ID; for ComfyUI: workflow-specific)
            speed: Speech speed multiplier (1.0 = normal, >1.0 = faster, <1.0 = slower)
            inference_mode: Override inference mode ("local" or "comfyui", default: from config)
            output_path: Custom output path (auto-generated if None)
            **params: Additional workflow parameters
        
        Returns:
            Generated audio file path
        
        Examples:
            # Local inference (Edge TTS)
            audio_path = await pixelle_video.tts(
                text="Hello, world!",
                inference_mode="local",
                voice="zh-CN-YunjianNeural",
                speed=1.2
            )
            
            # ComfyUI inference
            audio_path = await pixelle_video.tts(
                text="你好，世界！",
                inference_mode="comfyui",
                workflow="runninghub/tts_edge.json"
            )
        """
        # Determine inference mode (param > config)
        mode = inference_mode or self.config.get("inference_mode", "local")
        
        # Route to appropriate implementation
        if mode == "local":
            return await self._call_local_tts(
                text=text,
                voice=voice,
                speed=speed,
                output_path=output_path
            )
        else:  # comfyui
            # 1. Resolve workflow (returns structured info)
            workflow_info = self._resolve_workflow(workflow=workflow)
            
            # 2. Execute ComfyUI workflow
            return await self._call_comfyui_workflow(
                workflow_info=workflow_info,
                text=text,
                comfyui_url=comfyui_url,
                runninghub_api_key=runninghub_api_key,
                voice=voice,
                speed=speed,
                output_path=output_path,
                **params
            )
    
    async def _call_local_tts(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: Optional[float] = None,
        output_path: Optional[str] = None,
    ) -> str:
        """
        Generate speech using local Edge TTS
        
        Args:
            text: Text to convert to speech
            voice: Edge TTS voice ID (default: from config)
            speed: Speech speed multiplier (default: from config)
            output_path: Custom output path (auto-generated if None)
        
        Returns:
            Generated audio file path
        """
        # Get config defaults
        local_config = self.config.get("local", {})
        
        # Determine voice and speed (param > config)
        final_voice = voice or local_config.get("voice", "zh-CN-YunjianNeural")
        final_speed = speed if speed is not None else local_config.get("speed", 1.2)
        
        # Convert speed to rate parameter
        rate = speed_to_rate(final_speed)
        
        logger.info(f"🎙️  Using local Edge TTS: voice={final_voice}, speed={final_speed}x (rate={rate})")
        
        # Generate output path if not provided
        if not output_path:
            # Generate unique filename
            unique_id = uuid.uuid4().hex
            output_path = f"output/{unique_id}.mp3"
            
            # Ensure output directory exists
            Path("output").mkdir(parents=True, exist_ok=True)
        
        # Call Edge TTS
        try:
            audio_bytes = await edge_tts(
                text=text,
                voice=final_voice,
                rate=rate,
                output_path=output_path
            )
            
            logger.info(f"✅ Generated audio (local Edge TTS): {output_path}")
            return output_path
        
        except Exception as e:
            logger.error(f"Local TTS generation error: {e}")
            raise
    
    async def _call_comfyui_workflow(
        self,
        workflow_info: dict,
        text: str,
        comfyui_url: Optional[str] = None,
        runninghub_api_key: Optional[str] = None,
        voice: Optional[str] = None,
        speed: float = 1.0,
        output_path: Optional[str] = None,
        **params
    ) -> str:
        """
        Generate speech using ComfyUI workflow
        
        Args:
            workflow_info: Workflow info dict from _resolve_workflow()
            text: Text to convert to speech
            comfyui_url: ComfyUI URL
            runninghub_api_key: RunningHub API key
            voice: Voice ID (workflow-specific)
            speed: Speech speed multiplier (workflow-specific)
            output_path: Custom output path (downloads if URL returned)
            **params: Additional workflow parameters
        
        Returns:
            Generated audio file path (local if output_path provided, otherwise URL)
        """
        logger.info(f"🎙️  Using workflow: {workflow_info['key']}")
        
        # 1. Build workflow parameters (ComfyKit config is now managed by core)
        workflow_params = {"text": text}
        
        # Add optional TTS parameters (only if explicitly provided and not None)
        if voice is not None:
            workflow_params["voice"] = voice
        if speed is not None and speed != 1.0:
            workflow_params["speed"] = speed
        
        # Handle ref_audio parameter - convert to audio_file path format for workflow
        # For IndexTTS2 workflow, ref_audio is required, so use default if not provided
        if "ref_audio" in params and params["ref_audio"]:
            import shutil
            
            # If ref_audio is provided, convert to input directory path format
            ref_audio_path = params["ref_audio"]
            ref_audio_path_normalized = os.path.normpath(ref_audio_path)
            
            # Find ComfyUI input directory
            workflow_path = workflow_info.get("path", "")
            comfyui_input_dir = self._find_comfyui_input_dir(workflow_path)
            
            if comfyui_input_dir:
                # Ensure ComfyUI input directory exists
                os.makedirs(comfyui_input_dir, exist_ok=True)
                
                # Check if the provided path is an absolute path and file exists
                if os.path.isabs(ref_audio_path_normalized) and os.path.exists(ref_audio_path_normalized):
                    # Check if file is already in ComfyUI input directory
                    comfyui_input_dir_normalized = os.path.normpath(comfyui_input_dir)
                    if ref_audio_path_normalized.startswith(comfyui_input_dir_normalized):
                        # File is already in ComfyUI input directory
                        rel_path = os.path.relpath(ref_audio_path_normalized, comfyui_input_dir_normalized)
                        workflow_params["ref_audio"] = f"input/{rel_path.replace(os.sep, '/')}"
                    else:
                        # File is outside ComfyUI input directory - copy it
                        filename = os.path.basename(ref_audio_path_normalized)
                        target_path = os.path.join(comfyui_input_dir, filename)
                        
                        try:
                            shutil.copy2(ref_audio_path_normalized, target_path)
                            logger.info(f"Copied ref_audio file to ComfyUI input directory: {target_path}")
                            workflow_params["ref_audio"] = f"input/{filename}"
                        except Exception as e:
                            logger.error(f"Failed to copy ref_audio file to ComfyUI input directory: {e}")
                            raise Exception(f"TTS generation failed: Failed to copy reference audio file: {str(e)}")
                else:
                    # Relative path or file doesn't exist at provided path
                    # Try to resolve as relative path from current working directory
                    if not os.path.isabs(ref_audio_path_normalized):
                        # Try to find the file
                        possible_paths = [
                            ref_audio_path_normalized,
                            os.path.abspath(ref_audio_path_normalized),
                        ]
                        
                        source_path = None
                        for path in possible_paths:
                            if os.path.exists(path):
                                source_path = path
                                break
                        
                        if source_path:
                            # Copy to ComfyUI input directory
                            filename = os.path.basename(source_path)
                            target_path = os.path.join(comfyui_input_dir, filename)
                            
                            try:
                                shutil.copy2(source_path, target_path)
                                logger.info(f"Copied ref_audio file to ComfyUI input directory: {target_path}")
                                workflow_params["ref_audio"] = f"input/{filename}"
                            except Exception as e:
                                logger.error(f"Failed to copy ref_audio file: {e}")
                                raise Exception(f"TTS generation failed: Failed to copy reference audio file: {str(e)}")
                        else:
                            # Check if file already exists in ComfyUI input directory
                            filename = os.path.basename(ref_audio_path_normalized)
                            target_path = os.path.join(comfyui_input_dir, filename)
                            if os.path.exists(target_path):
                                workflow_params["ref_audio"] = f"input/{filename}"
                            else:
                                raise Exception(f"TTS generation failed: Reference audio file not found: {ref_audio_path}")
                    else:
                        # Absolute path but file doesn't exist
                        raise Exception(f"TTS generation failed: Reference audio file not found: {ref_audio_path}")
            else:
                # Could not find ComfyUI input directory - use path as-is (for RunningHub)
                if os.path.isabs(ref_audio_path_normalized):
                    filename = os.path.basename(ref_audio_path_normalized)
                    workflow_params["ref_audio"] = f"input/{filename}"
                else:
                    if not ref_audio_path.startswith("input/"):
                        workflow_params["ref_audio"] = f"input/{ref_audio_path}"
                    else:
                        workflow_params["ref_audio"] = ref_audio_path.replace("\\", "/")
        else:
            # No ref_audio provided - for IndexTTS2 workflow, we need to provide a default
            # Check if this is IndexTTS2 workflow by checking workflow path
            workflow_key = workflow_info.get("key", "")
            workflow_path = workflow_info.get("path", "")
            if "index" in workflow_key.lower() or "index" in workflow_path.lower():
                # For IndexTTS2, speaker_audio is required, so we need to set a default
                # Try to find a default audio file in input directory
                # First, try to find ComfyUI input directory
                comfyui_input_dir = None
                # Try multiple possible paths
                possible_paths = [
                    os.path.join(os.path.dirname(workflow_path), "..", "..", "ComfyUI", "input"),
                    os.path.join(os.path.dirname(workflow_path), "..", "..", "..", "ComfyUI", "input"),
                    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(workflow_path))), "ComfyUI", "input"),
                ]
                for path in possible_paths:
                    abs_path = os.path.abspath(path)
                    if os.path.exists(abs_path):
                        comfyui_input_dir = abs_path
                        break
                
                # Look for any audio file in input directory
                if comfyui_input_dir:
                    audio_files = [f for f in os.listdir(comfyui_input_dir) 
                                 if f.lower().endswith(('.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg'))]
                    if audio_files:
                        workflow_params["ref_audio"] = f"input/{audio_files[0]}"
                        logger.debug(f"Using default audio file for IndexTTS2: {workflow_params['ref_audio']}")
                    else:
                        logger.warning("No audio files found in ComfyUI input directory for IndexTTS2")
                else:
                    logger.warning("Could not find ComfyUI input directory for IndexTTS2 default audio")
        
        # Add any additional parameters (excluding ref_audio which we handled above)
        other_params = {k: v for k, v in params.items() if k != "ref_audio"}
        workflow_params.update(other_params)
        
        logger.debug(f"Workflow parameters: {workflow_params}")
        
        # 3. Execute workflow using shared ComfyKit instance from core
        try:
            # Get shared ComfyKit instance (lazy initialization + config hot-reload)
            kit = await self.core._get_or_create_comfykit()
            
            # Determine what to pass to ComfyKit based on source
            if workflow_info["source"] == "runninghub" and "workflow_id" in workflow_info:
                # RunningHub: pass workflow_id
                workflow_input = workflow_info["workflow_id"]
                logger.info(f"Executing RunningHub TTS workflow: {workflow_input}")
            else:
                # Selfhost: pass file path
                workflow_path = workflow_info["path"]
                logger.info(f"Executing selfhost TTS workflow: {workflow_path}")
                
                # For selfhost workflows with IndexTTS2, we need to modify the workflow JSON
                # to set audio_file in node 12 (VHS_LoadAudio) and remove _meta.title reference
                # ComfyKit parser sees $ref_audio.audio in _meta.title and expects ref_audio as parameter
                # Solution: Always modify workflow JSON for IndexTTS2 to remove _meta.title reference
                workflow_key = workflow_info.get("key", "")
                is_index_workflow = "index" in workflow_key.lower() or "index" in workflow_path.lower()
                
                should_modify_workflow = False
                audio_file_value = None
                
                if "ref_audio" in workflow_params:
                    # Use provided ref_audio - extract relative path from input/ (VHS_LoadAudio expects relative path)
                    ref_audio_path = workflow_params["ref_audio"].replace("\\", "/")
                    # Remove "input/" prefix if present, VHS_LoadAudio will add it automatically
                    if ref_audio_path.startswith("input/"):
                        audio_file_value = ref_audio_path[6:]  # Remove "input/" prefix
                    else:
                        audio_file_value = ref_audio_path
                    # Ensure path uses forward slashes only
                    audio_file_value = audio_file_value.replace("\\", "/")
                    
                    # Verify the file exists in ComfyUI input directory
                    comfyui_input_dir = self._find_comfyui_input_dir(workflow_path)
                    
                    # Check if file exists
                    if comfyui_input_dir:
                        # Convert relative path to absolute path for verification
                        if "/" in audio_file_value:
                            # Path contains subdirectory (e.g., "temp/ref_audio.mp3")
                            file_path = os.path.join(comfyui_input_dir, audio_file_value.replace("/", os.sep))
                        else:
                            # Path is just filename
                            file_path = os.path.join(comfyui_input_dir, audio_file_value)
                        
                        if not os.path.exists(file_path):
                            error_msg = (
                                f"Reference audio file not found: {file_path}\n"
                                f"ComfyUI input directory: {comfyui_input_dir}\n"
                                f"Please ensure the file exists in the ComfyUI input directory.\n"
                                f"If your ComfyUI is installed in a different location, set COMFYUI_PATH environment variable."
                            )
                            logger.error(error_msg)
                            raise Exception(f"TTS generation failed: {error_msg}")
                        else:
                            logger.debug(f"Verified ref_audio file exists: {file_path}")
                    
                    should_modify_workflow = True
                    logger.debug(f"Using ref_audio path: {audio_file_value}")
                elif is_index_workflow:
                    # For IndexTTS2 without ref_audio, try to find a default audio file
                    comfyui_input_dir = self._find_comfyui_input_dir(workflow_path)
                    
                    # Look for any audio file in input directory (including subdirectories)
                    if comfyui_input_dir:
                        audio_files = []
                        # First, check root of input directory
                        for f in os.listdir(comfyui_input_dir):
                            file_path = os.path.join(comfyui_input_dir, f)
                            if os.path.isfile(file_path) and f.lower().endswith(('.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg')):
                                audio_files.append(f)
                        
                        # If no files in root, check subdirectories (like temp/)
                        if not audio_files:
                            for root, dirs, files in os.walk(comfyui_input_dir):
                                for f in files:
                                    if f.lower().endswith(('.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg')):
                                        # Get relative path from input directory
                                        rel_path = os.path.relpath(os.path.join(root, f), comfyui_input_dir)
                                        audio_files.append(rel_path.replace("\\", "/"))  # Use forward slashes
                                        break
                                if audio_files:
                                    break
                        
                        if audio_files:
                            # Use the first found audio file (relative path from input/)
                            audio_file_value = audio_files[0]
                            should_modify_workflow = True
                            logger.debug(f"Using default audio file for IndexTTS2: {audio_file_value}")
                        else:
                            # No audio file found - IndexTTS2 requires a reference audio
                            error_msg = (
                                "IndexTTS2 workflow requires a reference audio file. "
                                f"Please provide 'ref_audio' parameter or place an audio file in ComfyUI input directory: {comfyui_input_dir}"
                            )
                            logger.error(error_msg)
                            raise Exception(f"TTS generation failed: {error_msg}")
                    else:
                        # ComfyUI input directory not found
                        error_msg = (
                            "IndexTTS2 workflow requires a reference audio file, but ComfyUI input directory could not be found. "
                            "Please either:\n"
                            "1. Provide 'ref_audio' parameter when calling TTS\n"
                            "2. Set COMFYUI_PATH environment variable to your ComfyUI installation directory\n"
                            "3. Place an audio file in your ComfyUI input directory"
                        )
                        logger.error(error_msg)
                        raise Exception(f"TTS generation failed: {error_msg}")
                
                # For IndexTTS2, always modify workflow to remove _meta.title reference
                # and set audio_file if we have a value
                if is_index_workflow or should_modify_workflow:
                    # Load workflow JSON and modify node 12
                    try:
                        with open(workflow_path, 'r', encoding='utf-8') as f:
                            workflow_json = json.load(f)
                        
                        # Modify node 12 (VHS_LoadAudio)
                        if "12" in workflow_json:
                            # Set audio_file if we have a value
                            if audio_file_value and "inputs" in workflow_json["12"]:
                                # On Windows, VHS_LoadAudio may expect backslashes for subdirectory paths
                                # Convert forward slashes to backslashes for Windows compatibility
                                if os.name == 'nt':  # Windows
                                    audio_file_for_workflow = audio_file_value.replace("/", "\\")
                                else:
                                    audio_file_for_workflow = audio_file_value
                                workflow_json["12"]["inputs"]["audio_file"] = audio_file_for_workflow
                                logger.debug(f"Set audio_file in workflow: {audio_file_for_workflow}")
                            
                            # Always remove _meta.title reference to prevent ComfyKit from expecting ref_audio parameter
                            if "_meta" in workflow_json["12"] and "title" in workflow_json["12"]["_meta"]:
                                # Remove the $ref_audio.audio reference to prevent ComfyKit from expecting it as parameter
                                if "$ref_audio.audio" in workflow_json["12"]["_meta"]["title"]:
                                    workflow_json["12"]["_meta"]["title"] = "Load Audio"
                        
                        # Save modified workflow to a temporary file
                        import tempfile
                        temp_dir = os.path.join(os.path.dirname(workflow_path), "temp")
                        os.makedirs(temp_dir, exist_ok=True)
                        temp_file = os.path.join(temp_dir, f"workflow_{uuid.uuid4().hex[:8]}.json")
                        with open(temp_file, 'w', encoding='utf-8') as f:
                            json.dump(workflow_json, f, ensure_ascii=False, indent=2)
                        workflow_input = temp_file
                        logger.debug(f"Created temporary workflow file: {temp_file}")
                    except Exception as e:
                        logger.warning(f"Failed to modify workflow JSON: {e}, using original workflow")
                        workflow_input = workflow_path
                else:
                    workflow_input = workflow_path
            
            result = await kit.execute(workflow_input, workflow_params)
            
            # 4. Handle result
            if result.status != "completed":
                error_msg = result.msg or "Unknown error"
                logger.error(f"TTS generation failed: {error_msg}")
                raise Exception(f"TTS generation failed: {error_msg}")
            
            # ComfyKit result can have audio files in different output types
            # Try to get audio file path from result
            audio_path = None
            
            # Check for audio files in result.audios (if available)
            if hasattr(result, 'audios') and result.audios:
                audio_path = result.audios[0]
                logger.debug(f"✅ Found audio in result.audios: {audio_path}")
            # Check for files in result.files
            elif hasattr(result, 'files') and result.files:
                audio_path = result.files[0]
                logger.debug(f"✅ Found audio in result.files: {audio_path}")
            # Check in outputs dictionary
            elif hasattr(result, 'outputs') and result.outputs:
                logger.debug(f"Searching for audio file in result.outputs: {result.outputs}")
                # Try to find audio file in outputs
                for key, value in result.outputs.items():
                    if isinstance(value, str) and any(value.endswith(ext) for ext in ['.mp3', '.wav', '.flac']):
                        audio_path = value
                        logger.debug(f"✅ Found audio in result.outputs[{key}]: {audio_path}")
                        break
            
            if not audio_path:
                logger.error("No audio file generated")
                logger.error(f"❌ Result analysis:")
                logger.error(f"   - result.audios: {getattr(result, 'audios', 'NOT_FOUND')}")
                logger.error(f"   - result.files: {getattr(result, 'files', 'NOT_FOUND')}")
                logger.error(f"   - result.outputs: {getattr(result, 'outputs', 'NOT_FOUND')}")
                logger.error(f"   - Full __dict__: {result.__dict__}")
                raise Exception("No audio file generated by workflow")
            
            # If output_path provided and audio_path is URL, download to local
            if output_path and audio_path.startswith(('http://', 'https://')):
                import httpx
                
                # Ensure parent directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                logger.info(f"Downloading audio from {audio_path} to {output_path}")
                async with httpx.AsyncClient() as client:
                    response = await client.get(audio_path)
                    response.raise_for_status()
                    
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                
                logger.info(f"✅ Generated audio (ComfyUI): {output_path}")
                return output_path
            
            logger.info(f"✅ Generated audio (ComfyUI): {audio_path}")
            return audio_path
        
        except Exception as e:
            logger.error(f"TTS generation error: {e}")
            raise
