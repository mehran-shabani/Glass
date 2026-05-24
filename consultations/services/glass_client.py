import json
from typing import Optional
import requests
from django.conf import settings

class GlassClientError(Exception): pass
class GlassAuthenticationError(GlassClientError): pass
class GlassBadRequestError(GlassClientError): pass
class GlassRateLimitError(GlassClientError): pass
class GlassServerError(GlassClientError): pass
class GlassTimeoutError(GlassClientError): pass

PROMPT_TEMPLATE="""You are assisting a licensed clinician. This is clinician-facing clinical decision support, not direct patient advice.

Patient context:
{patient_context}

Clinical task type:
{task_type}

Clinical question:
{question}

Return a structured, evidence-based answer with:
1. Bottom line
2. Key clinical reasoning
3. Differential diagnosis if relevant
4. Recommended next steps
5. Red flags / urgent actions
6. Missing data and limitations
7. References/citations if available from the API

Important safety note:
The output is a draft for clinician review and must not replace clinical judgment, local guidelines, examination, or emergency care.
"""

class GlassClient:
    def _headers(self)->dict:
        return {'Authorization':f'Bearer {settings.GLASS_API_KEY}','Content-Type':'application/json'}
    def send_messages(self,messages:list[dict],version:Optional[str]=None)->dict:
        if not settings.GLASS_API_KEY:
            raise GlassAuthenticationError('Missing GLASS_API_KEY.')
        url=f"{settings.GLASS_API_BASE_URL.rstrip('/')}/messages"
        payload={'version':version or settings.GLASS_API_VERSION,'messages':messages}
        try:
            resp=requests.post(url,headers=self._headers(),json=payload,timeout=settings.GLASS_API_TIMEOUT_SECONDS)
        except requests.Timeout as e:
            raise GlassTimeoutError('Glass API request timed out.') from e
        except requests.RequestException as e:
            raise GlassClientError(f'Glass API request failed: {e}') from e
        body=(resp.text or '')[:1000]
        if resp.status_code==400: raise GlassBadRequestError(body)
        if resp.status_code in (401,403): raise GlassAuthenticationError(body)
        if resp.status_code==429: raise GlassRateLimitError(body)
        if resp.status_code in (500,502,503,504): raise GlassServerError(body)
        try:
            return resp.json()
        except ValueError as e:
            raise GlassClientError('Glass API returned non-JSON response.') from e
    def ask_clinical_question(self,question:str,patient_context:str='',task_type:str='clinical_qa')->dict:
        prompt=PROMPT_TEMPLATE.format(patient_context=patient_context or '(none provided)',task_type=task_type,question=question)
        return self.send_messages([{'role':'user','content':prompt}])
