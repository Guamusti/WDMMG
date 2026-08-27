import madridTuition from '../../data/processed/tuition/madrid-2025-2026.json';

export const tuitionSource = madridTuition;

export function tuitionForOffer(offer) {
  const university = madridTuition.knownOfferLevels[offer?.short];
  if (!university) return null;
  const level = university.exceptions[offer.degree] || university.default;
  const perCredit = madridTuition.firstEnrollmentPerCredit[String(level)];
  return { level, perCredit, academicYear: madridTuition.academicYear, credits: madridTuition.creditsPerAcademicYear, annual: perCredit * madridTuition.creditsPerAcademicYear, source: madridTuition.source, sourceUrl: madridTuition.sourceUrl, limitations: madridTuition.limitations };
}
